import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from ultralytics import YOLO
import cv2
import os

class TrafikLevhasiApp:
    def __init__(self):
        #pencere
        self.root = ctk.CTk()
        self.root.title("Trafik Levhası Tespiti")
        self.root.geometry("1000x700")

        import os
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_dir, "model", "yolo26n.pt")
    
        print(f"Model yolu: {model_path}")
        print(f"Model var mı? {os.path.exists(model_path)}")
        
        self.model = YOLO(model_path)
    
        # Model sınıflarını yazdır (KONTROL İÇİN)
        print("Model sınıfları:", self.model.names)

        self.image_path = None

        #arayüz oluşturma
        self.create_ui()

    def create_ui(self):
        #başlık
        title = ctk.CTkLabel(
            self.root,
            text = "YOLO Trafik Levhası Tespit Sistemi",
            font = ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)

        #ana çerçeve iki sütunlu
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(pady=20, padx=10, fill="both", expand=True)

        #sık sütunda orijinal görsel
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.original_label = ctk.CTkLabel(
            left_frame,
            text = "görsel yüklenmedi",
            font = ctk.CTkFont(size=14)
        )
        self.original_label.pack(pady=10)

        #sağ sütunda sonuç görseli
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.result_label = ctk.CTkLabel(
            right_frame,
            text = "sonuç görseli",
            font = ctk.CTkFont(size=14)
        )
        self.result_label.pack(pady=10)

        #butonlar
        button_frame = ctk.CTkFrame(self.root)
        button_frame.pack(pady=20)

        #görsel seçme butonu
        self.selected_btn = ctk.CTkButton(
            button_frame,
            text = "Görsel Seç",
            command = self.select_image,
            font = ctk.CTkFont(size=16),
            width = 150,
            height = 40
        )
        self.selected_btn.pack(side="left", padx=10)

        #tespit etme butonu
        self.detect_btn = ctk.CTkButton(
            button_frame,
            text="Tespit Et",
            command=self.detect_objects,
            font=ctk.CTkFont(size=16),
            width=150,
            height=40,
            state="disabled"  # Başlangıçta pasif
        )
        self.detect_btn.pack(side="left", padx=10)

        # Sonuç listesi
        result_frame = ctk.CTkFrame(self.root)
        result_frame.pack(padx=20, pady=10, fill="x")
        
        self.result_text = ctk.CTkTextbox(
            result_frame,
            height=100,
            font=ctk.CTkFont(size=14)
        )
        self.result_text.pack(pady=10, padx=10, fill="x")
        self.result_text.insert("1.0", "Tespit edilen trafik levhaları burada görünecek...")
        
    def select_image(self):
        # Dosya seçme penceresi
        file_path = filedialog.askopenfilename(
            title="Görsel Seç",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        
        if file_path:
            self.image_path = file_path
            
            # Görseli yükle ve göster
            img = Image.open(file_path)
            img = img.resize((400, 400))  # Boyutlandır
            photo = ImageTk.PhotoImage(img)
            
            self.original_label.configure(image=photo, text="")
            self.original_label.image = photo  # Referansı sakla
            
            # Tespit et butonunu aktif et
            self.detect_btn.configure(state="normal")
            
            # Sonuç alanını temizle
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", "Görsel yüklendi. 'Tespit Et' butonuna basın.")
            
            # Sonuç görselini sıfırla
            self.result_label.configure(image="", text="Sonuç Görseli")
    
    def detect_objects(self):
        if not self.image_path:
            messagebox.showwarning("Uyarı", "Lütfen önce bir görsel seçin!")
            return
        
        # YOLO ile tespit yap
        results = self.model(self.image_path)
        
        # Sonuçları işle
        detected_classes = []
        
        # Sonuç görselini çiz
        result_image = results[0].plot()  # Bounding box'lı görsel
        
        # OpenCV formatından PIL formatına çevir
        result_image_rgb = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
        result_pil = Image.fromarray(result_image_rgb)
        result_pil = result_pil.resize((400, 400))
        result_photo = ImageTk.PhotoImage(result_pil)
        
        # Sonuç görselini göster
        self.result_label.configure(image=result_photo, text="")
        self.result_label.image = result_photo
        
        # Tespit edilen sınıfları al
        for box in results[0].boxes:
            class_id = int(box.cls[0])
            class_name = self.model.names[class_id]
            confidence = float(box.conf[0]) * 100
            detected_classes.append(f"{class_name} (%{confidence:.1f})")
        
        # Sonuçları yaz
        self.result_text.delete("1.0", "end")
        
        if detected_classes:
            result_message = "Tespit edilen trafik levhaları:\n"
            for i, cls in enumerate(detected_classes, 1):
                result_message += f"{i}. {cls}\n"
            self.result_text.insert("1.0", result_message)
        else:
            self.result_text.insert("1.0", "Trafik levhası tespit edilemedi.")
    
    def run(self):
        self.root.mainloop()

# Uygulamayı başlat
if __name__ == "__main__":
    app = TrafikLevhasiApp()
    app.run()