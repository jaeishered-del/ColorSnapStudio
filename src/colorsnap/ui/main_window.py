from __future__ import annotations
import sys
from pathlib import Path
from PySide6.QtCore import Qt, QThread, Signal, QObject
from PySide6.QtGui import QPixmap, QColor, QAction, QShortcut, QKeySequence, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QLabel,QFrame,
 QStackedWidget,QFileDialog,QSpinBox,QLineEdit,QListWidget,QListWidgetItem,QMessageBox,QColorDialog,
 QComboBox,QGridLayout,QScrollArea,QStatusBar,QInputDialog,QCheckBox,QTextEdit,QToolButton)
from .. import __version__
from ..core.colors import normalize_hex, hex_to_rgb, hex_to_hsl, format_rgb, format_hsl, harmonies, check_contrast, best_text_on
from ..core.extraction import extract_dominant_colors, SUPPORTED
from ..core.models import Palette, ColorEntry
from ..services.storage import load_library, save_library, load_settings, save_settings, LibraryError
from ..services.exporters import export_palette
from .theme import STYLESHEET, LIGHT_STYLESHEET

class Worker(QObject):
    finished=Signal(object); failed=Signal(str)
    def __init__(self,path,count): super().__init__(); self.path=path; self.count=count
    def run(self):
        try: self.finished.emit(extract_dominant_colors(self.path,self.count))
        except Exception as e: self.failed.emit(str(e))

class ColorCard(QFrame):
    changed=Signal(); removed=Signal(object)
    def __init__(self, entry: ColorEntry, parent=None):
        super().__init__(parent); self.entry=entry; self.setObjectName("card"); self.setMinimumWidth(170)
        lay=QVBoxLayout(self)
        self.swatch=QPushButton(); self.swatch.setFixedHeight(72); self._paint(); self.swatch.setToolTip("Click to edit with color picker")
        self.swatch.clicked.connect(self.pick)
        lay.addWidget(self.swatch)
        self.name_edit=QLineEdit(entry.name); self.name_edit.editingFinished.connect(self._rename)
        lay.addWidget(self.name_edit)
        self.hex_edit=QLineEdit(entry.hex); self.hex_edit.editingFinished.connect(self._hex_changed)
        lay.addWidget(self.hex_edit)
        self.detail=QLabel(); self._labels(); lay.addWidget(self.detail)
        row=QHBoxLayout()
        for label, fn in [("HEX",lambda: self._copy(self.entry.hex)),("RGB",lambda: self._copy(format_rgb(self.entry.hex))),("HSL",lambda: self._copy(format_hsl(self.entry.hex)))]:
            b=QPushButton(label); b.setToolTip(f"Copy {label}"); b.clicked.connect(fn); row.addWidget(b)
        lay.addLayout(row)
        up=QPushButton("←"); up.setToolTip("Move left"); up.clicked.connect(lambda: self._move(-1)); lay.addWidget(up)
        down=QPushButton("→"); down.setToolTip("Move right"); down.clicked.connect(lambda: self._move(1)); lay.addWidget(down)
        rm=QPushButton("Remove"); rm.clicked.connect(lambda: self.removed.emit(self)); lay.addWidget(rm)
    def _paint(self): self.swatch.setStyleSheet(f"background:{self.entry.hex};border-radius:10px;border:1px solid #444")
    def _labels(self):
        r,g,b=hex_to_rgb(self.entry.hex); h,s,l=hex_to_hsl(self.entry.hex)
        self.detail.setText(f"RGB {r}, {g}, {b}\nHSL {h}°, {s}%, {l}%")
    def _copy(self,text):
        QApplication.clipboard().setText(text); w=self.window(); 
        if hasattr(w,"toast"): w.toast(f"Copied {text}")
    def pick(self):
        c=QColorDialog.getColor(QColor(self.entry.hex), self, "Choose color")
        if c.isValid(): self.entry.hex=c.name().upper(); self.hex_edit.setText(self.entry.hex); self._sync()
    def _rename(self): self.entry.name=self.name_edit.text().strip() or self.entry.name; self.changed.emit()
    def _hex_changed(self):
        try: self.entry.hex=normalize_hex(self.hex_edit.text())
        except ValueError as e: QMessageBox.warning(self,"Invalid HEX",str(e)); self.hex_edit.setText(self.entry.hex); return
        self._sync()
    def _move(self,d):
        w=self.window()
        if hasattr(w,"move_card"): w.move_card(self,d)
    def _sync(self): self._paint(); self._labels(); self.hex_edit.setText(self.entry.hex); self.changed.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle(f"ColorSnap Studio {__version__}"); self.resize(1220,780); self.setAcceptDrops(True)
        self.settings=load_settings(); self.current_palette=Palette(name="Untitled Palette"); self.cards=[]; self.source_path=None
        try: self.library=load_library()
        except LibraryError as e: self.library=[]; QMessageBox.warning(self,"Library",str(e))
        self._build(); self.apply_theme(self.settings.get("theme","dark")); self.refresh_library(); self.show_empty()
        self.statusBar().showMessage("Ready — open or drop an image to begin (processing is 100% local).")
        QShortcut(QKeySequence("Ctrl+O"),self).activated.connect(self.open_image_dialog)
        QShortcut(QKeySequence("Ctrl+S"),self).activated.connect(self.save_current_to_library)
        QShortcut(QKeySequence("Ctrl+E"),self).activated.connect(lambda: self.export_dialog("json"))

    def _build(self):
        central=QWidget(); self.setCentralWidget(central); root=QHBoxLayout(central); root.setContentsMargins(0,0,0,0)
        side=QFrame(); side.setObjectName("sidebar"); side.setFixedWidth(210); sl=QVBoxLayout(side)
        title=QLabel("🎨 ColorSnap"); title.setStyleSheet("font-size:19px;font-weight:700"); sl.addWidget(title)
        sub=QLabel("Studio"); sub.setObjectName("subtitle"); sl.addWidget(sub)
        self.nav_buttons=[]
        pages=[("🏠  Studio",0),("📚  Library",1),("◐  Contrast",2),("✦  Harmonies",3),("⚙  Settings",4),("ℹ  About",5)]
        for label,idx in pages:
            b=QPushButton(label); b.setObjectName("nav"); b.setCheckable(True); b.clicked.connect(lambda _,i=idx: self.switch_page(i)); sl.addWidget(b); self.nav_buttons.append(b)
        sl.addStretch(); sl.addWidget(QLabel(f"v{__version__} • Local only")); root.addWidget(side)
        self.stack=QStackedWidget(); root.addWidget(self.stack,1)
        self.stack.addWidget(self._studio_page()); self.stack.addWidget(self._library_page()); self.stack.addWidget(self._contrast_page()); self.stack.addWidget(self._harmony_page()); self.stack.addWidget(self._settings_page()); self.stack.addWidget(self._about_page())
        self.switch_page(0); self.setStatusBar(QStatusBar())

    def switch_page(self,i):
        self.stack.setCurrentIndex(i)
        for j,b in enumerate(self.nav_buttons): b.setChecked(j==i)

    # Studio
    def _studio_page(self):
        w=QWidget(); lay=QVBoxLayout(w)
        t=QLabel("Studio"); t.setObjectName("title"); lay.addWidget(t)
        bar=QHBoxLayout()
        openb=QPushButton("Open Image…"); openb.setObjectName("primary"); openb.clicked.connect(self.open_image_dialog); bar.addWidget(openb)
        bar.addWidget(QLabel("Colors:"))
        self.count_spin=QSpinBox(); self.count_spin.setRange(3,16); self.count_spin.setValue(int(self.settings.get("default_count",6))); bar.addWidget(self.count_spin)
        self.re_btn=QPushButton("Re-extract"); self.re_btn.clicked.connect(self.start_extract); bar.addWidget(self.re_btn)
        addb=QPushButton("＋ Add Color"); addb.clicked.connect(self.add_color); bar.addWidget(addb)
        copyall=QPushButton("Copy All HEX"); copyall.clicked.connect(self.copy_all); bar.addWidget(copyall)
        bar.addStretch(); lay.addLayout(bar)
        name_row=QHBoxLayout(); name_row.addWidget(QLabel("Palette name:")); self.palette_name=QLineEdit(self.current_palette.name); name_row.addWidget(self.palette_name); lay.addLayout(name_row)
        self.image_label=QLabel("Drop an image here, or click Open Image.\nSupported: PNG • JPG • WEBP • BMP\n\nYour images never leave this device.")
        self.image_label.setAlignment(Qt.AlignCenter); self.image_label.setMinimumHeight(260); self.image_label.setObjectName("card"); lay.addWidget(self.image_label)
        self.source_label=QLabel("No image loaded"); self.source_label.setObjectName("muted"); lay.addWidget(self.source_label)
        saveb=QPushButton("Save Palette to Library (Ctrl+S)"); saveb.clicked.connect(self.save_current_to_library); lay.addWidget(saveb)
        exp_row=QHBoxLayout()
        for fmt in ["json","css","scss","txt"]:
            b=QPushButton(f"Export .{fmt}"); b.clicked.connect(lambda _,f=fmt: self.export_dialog(f)); exp_row.addWidget(b)
        lay.addLayout(exp_row)
        scroll=QScrollArea(); scroll.setWidgetResizable(True); self.palette_host=QWidget(); self.palette_layout=QGridLayout(self.palette_host); scroll.setWidget(self.palette_host); lay.addWidget(scroll,1)
        return w

    def _library_page(self):
        w=QWidget(); lay=QVBoxLayout(w); t=QLabel("Palette Library"); t.setObjectName("title"); lay.addWidget(t)
        self.lib_list=QListWidget(); lay.addWidget(self.lib_list)
        row=QHBoxLayout()
        for label,fn in [("Load",self.load_selected),("Rename",self.rename_selected),("Delete",self.delete_selected)]:
            b=QPushButton(label); b.clicked.connect(fn); row.addWidget(b)
        lay.addLayout(row); lay.addWidget(QLabel("Palettes are stored locally as versioned JSON in your user data folder."))
        return w

    def _contrast_page(self):
        w=QWidget(); lay=QVBoxLayout(w); t=QLabel("WCAG Contrast Checker"); t.setObjectName("title"); lay.addWidget(t)
        lay.addWidget(QLabel("Foreground")); self.fg_edit=QLineEdit("#FFFFFF"); lay.addWidget(self.fg_edit)
        lay.addWidget(QLabel("Background")); self.bg_edit=QLineEdit("#7C3AED"); lay.addWidget(self.bg_edit)
        b=QPushButton("Check Contrast"); b.setObjectName("primary"); b.clicked.connect(self.run_contrast); lay.addWidget(b)
        self.contrast_preview=QLabel("Sample text — The quick brown fox jumps over the lazy dog."); self.contrast_preview.setAlignment(Qt.AlignCenter); self.contrast_preview.setMinimumHeight(80); lay.addWidget(self.contrast_preview)
        self.contrast_result=QLabel("Enter two HEX colors and click Check."); lay.addWidget(self.contrast_result)
        lay.addWidget(QLabel("Note: this checker aids design decisions; it does not replace full accessibility testing with real users and assistive technology."))
        lay.addStretch(); self.run_contrast(); return w

    def _harmony_page(self):
        w=QWidget(); lay=QVBoxLayout(w); t=QLabel("Color Harmonies"); t.setObjectName("title"); lay.addWidget(t)
        lay.addWidget(QLabel("Base HEX")); self.base_edit=QLineEdit("#7C3AED"); lay.addWidget(self.base_edit)
        b=QPushButton("Generate Suggestions"); b.setObjectName("primary"); b.clicked.connect(self.run_harmonies); lay.addWidget(b)
        self.harmony_text=QTextEdit(); self.harmony_text.setReadOnly(True); lay.addWidget(self.harmony_text)
        add=QPushButton("Add First Suggestion Set to Palette"); add.clicked.connect(self.add_harmony_to_palette); lay.addWidget(add); self.run_harmonies(); return w

    def _settings_page(self):
        w=QWidget(); lay=QVBoxLayout(w); t=QLabel("Settings"); t.setObjectName("title"); lay.addWidget(t)
        lay.addWidget(QLabel("Theme")); self.theme_combo=QComboBox(); self.theme_combo.addItems(["dark","light"]); self.theme_combo.setCurrentText(self.settings.get("theme","dark")); lay.addWidget(self.theme_combo)
        lay.addWidget(QLabel("Default color count (3-16)")); self.def_spin=QSpinBox(); self.def_spin.setRange(3,16); self.def_spin.setValue(int(self.settings.get("default_count",6))); lay.addWidget(self.def_spin)
        b=QPushButton("Save Settings"); b.setObjectName("primary"); b.clicked.connect(self.save_settings_ui); lay.addWidget(b); lay.addStretch(); return w

    def _about_page(self):
        w=QWidget(); lay=QVBoxLayout(w); t=QLabel("About ColorSnap Studio"); t.setObjectName("title"); lay.addWidget(t)
        txt=QLabel(f"Version {__version__}\n\nExtract dominant colors from images, build palettes, check WCAG contrast, and export design tokens — fully offline.\n\nBuilt with Python, PySide6, Pillow and NumPy. Licensed under MIT (see LICENSE).\n\nPrivacy: images are processed locally and are never uploaded.\n\nShortcuts: Ctrl+O Open image • Ctrl+S Save palette • Ctrl+E Export JSON\nDrag & drop: drop PNG/JPG/WEBP/BMP anywhere in the window.")
        txt.setWordWrap(True); lay.addWidget(txt); lay.addStretch(); return w

    # Actions
    def toast(self,msg): self.statusBar().showMessage(msg,4000)
    def apply_theme(self,name): self.setStyleSheet(LIGHT_STYLESHEET if name=="light" else STYLESHEET)
    def save_settings_ui(self):
        self.settings={"theme":self.theme_combo.currentText(),"default_count":self.def_spin.value()}; save_settings(self.settings); self.count_spin.setValue(self.def_spin.value()); self.apply_theme(self.settings["theme"]); self.toast("Settings saved.")
    def open_image_dialog(self):
        path,_=QFileDialog.getOpenFileName(self,"Open Image","","Images (*.png *.jpg *.jpeg *.webp *.bmp)")
        if path: self.load_image_file(path)
    def dragEnterEvent(self,e:QDragEnterEvent):
        if e.mimeData().hasUrls(): e.acceptProposedAction()
    def dropEvent(self,e:QDropEvent):
        urls=e.mimeData().urls()
        if urls: self.load_image_file(urls[0].toLocalFile())
    def load_image_file(self,path):
        if Path(path).suffix.lower() not in SUPPORTED: QMessageBox.warning(self,"Unsupported file","Please choose PNG, JPG, JPEG, WEBP or BMP."); return
        pix=QPixmap(path)
        if pix.isNull(): QMessageBox.critical(self,"Invalid image","This file could not be read as an image. It may be corrupt or not a real image file."); return
        self.source_path=path; self.source_label.setText(f"Source: {Path(path).name}  •  {pix.width()}×{pix.height()}")
        self.image_label.setPixmap(pix.scaled(760,320,Qt.KeepAspectRatio,Qt.SmoothTransformation)); self.start_extract()
    def start_extract(self):
        if not self.source_path: 
            if self.cards: return
            QMessageBox.information(self,"No image","Open an image first, or add colors manually with ＋ Add Color."); return
        # Prevent overlapping workers: a second extraction must not overwrite the
        # thread/worker references while the first worker is still running.
        if getattr(self, "_extracting", False):
            return
        self._extracting = True
        self.re_btn.setEnabled(False)
        self.toast("Extracting colors…")
        self.thread = QThread(self)
        self.worker = Worker(self.source_path, self.count_spin.value())
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._extracted)
        self.worker.failed.connect(self._extraction_failed)
        self.worker.finished.connect(self.thread.quit)
        self.worker.failed.connect(self.thread.quit)
        self.thread.finished.connect(self._extraction_finished)
        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.start()

    def _extraction_failed(self, message):
        QMessageBox.critical(self, "Extraction failed", message)

    def _extraction_finished(self):
        self._extracting = False
        self.re_btn.setEnabled(True)
        self.worker = None
        self.thread = None
    def _extracted(self,colors):
        self.current_palette.colors=list(colors); self.current_palette.source_image=Path(self.source_path).name if self.source_path else None; self.rebuild_cards(); self.toast(f"Extracted {len(colors)} colors.")
    def rebuild_cards(self):
        # Remove old layout items as well as widgets; otherwise repeated edits
        # leave orphaned QLayoutItems behind and the palette grid grows stale.
        while self.palette_layout.count():
            item = self.palette_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
        self.cards = []
        for i, entry in enumerate(self.current_palette.colors):
            card = ColorCard(entry)
            card.removed.connect(self.remove_card)
            card.changed.connect(self.sync_from_cards)
            self.cards.append(card)
            self.palette_layout.addWidget(card, i // 4, i % 4)
    def sync_from_cards(self): self.current_palette.colors=[c.entry for c in self.cards]
    def move_card(self,card,d):
        i=self.cards.index(card); j=i+d
        if 0<=j<len(self.cards): self.cards[i],self.cards[j]=self.cards[j],self.cards[i]; self.sync_from_cards(); self.rebuild_cards()
    def remove_card(self,card):
        self.cards.remove(card); card.setParent(None); self.sync_from_cards(); self.rebuild_cards()
    def add_color(self):
        c=QColorDialog.getColor(QColor("#7C3AED"),self,"Add color")
        if c.isValid(): self.current_palette.colors.append(ColorEntry(c.name().upper())); self.rebuild_cards()
    def copy_all(self):
        if not self.cards: self.toast("No colors to copy."); return
        QApplication.clipboard().setText(", ".join(c.entry.hex for c in self.cards)); self.toast("Copied all HEX values.")
    def show_empty(self): self.rebuild_cards()
    def _palette_from_ui(self) -> Palette:
        self.current_palette.name=self.palette_name.text().strip() or "Untitled Palette"; self.sync_from_cards(); return self.current_palette
    def save_current_to_library(self):
        p=self._palette_from_ui()
        if not p.colors: QMessageBox.information(self,"Empty palette","Add or extract colors before saving."); return
        # replace same-name or append copy
        import copy; self.library=[x for x in self.library if x.name!=p.name]; self.library.append(copy.deepcopy(p))
        try: save_library(self.library)
        except Exception as e: QMessageBox.critical(self,"Save failed",str(e)); return
        self.refresh_library(); self.toast(f"Saved '{p.name}' to library.")
    def refresh_library(self):
        if not hasattr(self,"lib_list"): return
        self.lib_list.clear()
        for p in self.library: self.lib_list.addItem(f"{p.name}  —  {len(p.colors)} colors  —  {p.created_at[:10]}")
    def _selected_palette(self):
        i=self.lib_list.currentRow(); return self.library[i] if 0<=i<len(self.library) else None
    def load_selected(self):
        p=self._selected_palette()
        if p: import copy; self.current_palette=copy.deepcopy(p); self.palette_name.setText(p.name); self.rebuild_cards(); self.switch_page(0)
    def rename_selected(self):
        p=self._selected_palette()
        if not p: return
        name,ok=QInputDialog.getText(self,"Rename palette","Name:",text=p.name)
        if ok and name.strip(): p.name=name.strip(); save_library(self.library); self.refresh_library()
    def delete_selected(self):
        p=self._selected_palette()
        if not p: return
        if QMessageBox.question(self,"Delete palette",f"Delete '{p.name}'?")==QMessageBox.Yes: self.library.remove(p); save_library(self.library); self.refresh_library()
    def export_dialog(self,fmt):
        p=self._palette_from_ui()
        if not p.colors: QMessageBox.information(self,"Empty palette","Nothing to export yet."); return
        default=f"{p.name.replace(' ','_')}_palette.{fmt}"
        path,_=QFileDialog.getSaveFileName(self,f"Export {fmt.upper()}",default)
        if not path: return
        try: export_palette(p,fmt,path); self.toast(f"Exported to {path}")
        except Exception as e: QMessageBox.critical(self,"Export failed",str(e))
    def run_contrast(self):
        try: fg=normalize_hex(self.fg_edit.text()); bg=normalize_hex(self.bg_edit.text())
        except Exception as e: self.contrast_result.setText(str(e)); return
        r=check_contrast(fg,bg); self.contrast_preview.setStyleSheet(f"background:{bg};color:{fg};font-size:16px;border-radius:10px")
        self.contrast_result.setText(r.summary()+"\nAA = 4.5:1 normal / 3:1 large • AAA = 7:1 normal / 4.5:1 large (WCAG 2.x)")
    def run_harmonies(self):
        try: base=normalize_hex(self.base_edit.text())
        except Exception as e: self.harmony_text.setPlainText(str(e)); return
        self._last_harmonies=harmonies(base)
        self.harmony_text.setPlainText("\n\n".join(f"{k}:\n  " + ", ".join(v) for k,v in self._last_harmonies.items()))
    def add_harmony_to_palette(self):
        self.run_harmonies()
        if hasattr(self,"_last_harmonies"):
            for hexv in self._last_harmonies["Complementary"]: self.current_palette.colors.append(ColorEntry(hexv))
            self.rebuild_cards(); self.switch_page(0)

def main(argv=None):
    app=QApplication(argv or sys.argv); app.setApplicationName("ColorSnap Studio"); app.setApplicationVersion(__version__); app.setOrganizationName("ColorSnap")
    win=MainWindow(); win.show(); return app.exec()
if __name__=="__main__": raise SystemExit(main())
