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

        self.root.configure(fg_color="#d38c9d")  # Arka plan rengini ayarlayın

        #imleç ekliyorum hadi bakalım, başına @ gelmek zorundaymış
        self.root.configure(cursor="@pink.cur")

        #modeli yükle
        self.model = YOLO("../model/best.pt")

        self.image_path = None

        #arayüz oluşturma
        self.create_ui()

    def create_ui(self):
        #başlık
        current_dir = os.path.dirname(os.path.abspath(__file__))
        left_path = os.path.join(current_dir, "Turkey.jpg")
        right_path = os.path.join(current_dir, "hehe.png")  # Sağ logo için yol
        
        # PIL ve CustomTkinter ile görseli hazırla
        pil_img = Image.open(left_path)
        left_img = ctk.CTkImage(
            light_image=pil_img,
            dark_image=pil_img,
            size=(70, 45)
        )

        pil_img_right = Image.open(right_path)
        right_img = ctk.CTkImage(
            light_image=pil_img_right,
            dark_image=pil_img_right,
            size=(65, 70)
        )

        # 2. Başlığı ve logoları tutacak ana şeffaf çerçeve
        title_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        title_frame.pack(pady=20)

        # 3. SOL TARAFTAKI LOGO
        left_logo_label = ctk.CTkLabel(
            title_frame,
            image=left_img,  
            text=""
        )
        left_logo_label.pack(side="left", padx=10)

        # 4. ORTADAKİ BAŞLIK YAZISI
        title_text = ctk.CTkLabel(
            title_frame,
            text=" YOLO Trafik Levhası Tespit Sistemi ",
            font=ctk.CTkFont(family="Comic Sans MS", size=32, weight="bold")
        )
        title_text.pack(side="left")

        # 5. SAĞ TARAFTAKİ LOGO (İstersen sağ için farklı bir `logo_img_right` de tanımlayabilirsin)
        right_logo_label = ctk.CTkLabel(
            title_frame,
            image=right_img,  
            text=""
        )
        right_logo_label.pack(side="left", padx=10)

        #ana çerçeve iki sütunlu
        main_frame = ctk.CTkFrame(self.root, fg_color="#f7dae7", border_width=0)
        main_frame.pack(pady=20, padx=10, fill="both", expand=True)

        #sık sütunda orijinal görsel
        left_frame = ctk.CTkFrame(main_frame, fg_color="#e2b4c1", border_width=2, border_color="#d38c9d")
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.original_label = ctk.CTkLabel(
            left_frame,
            text = "görsel yükleyin",
            font = ctk.CTkFont(size=14)
        )
        self.original_label.pack(pady=10)

        #sağ sütunda sonuç görseli
        right_frame = ctk.CTkFrame(main_frame, fg_color="#e2b4c1", border_width=2, border_color="#d38c9d")
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.result_label = ctk.CTkLabel(
            right_frame,
            text = "size ne olduğunu söyleyelim",
            font = ctk.CTkFont(size=14)
        )
        self.result_label.pack(pady=10)

        #butonlar
        button_frame = ctk.CTkFrame(self.root, fg_color="#d38c9d", border_width=0)
        button_frame.pack(pady=20)

        #görsel seçme butonu
        self.selected_btn = ctk.CTkButton(
            button_frame,
            text = "Görsel Seç",
            command = self.select_image,
            font = ctk.CTkFont(size=16),
            width = 200,
            height = 50,
            hover = False,
            cursor = "@cat3.cur",
            fg_color="#e2b4c1",         # Butonun rengi
            text_color="#a55166",       # Yazı rengi (Beyaz)
            #hover_color="#0f3460",      # Eğer hover'ı tekrar açarsan üzerine gelince olacak renk
            corner_radius=10,           # Daha yuvarlak, yumuşak köşeler
            border_width=3,             # Kenarlık kalınlığı
            border_color="#a55166"      # Kenarlık rengi
        )
        self.selected_btn.pack(side="left", padx=30)
        self.selected_btn.configure(cursor="@cat3.cur")

        #tespit etme butonu
        self.detect_btn = ctk.CTkButton(
            button_frame,
            text="Tespit Et",
            command=self.detect_objects,
            font=ctk.CTkFont(size=16),
            width=200,
            height=50,
            hover = False,
            cursor = "@cat2.cur",
            fg_color="#e2b4c1",         # Butonun rengi
            text_color="#a55166",       # Yazı rengi (Beyaz)
            #hover_color="#0f3460",      # Eğer hover'ı tekrar açarsan üzerine gelince olacak renk
            corner_radius=10,           # Daha yuvarlak, yumuşak köşeler
            border_width=3,             # Kenarlık kalınlığı
            border_color="#a55166",      # Kenarlık rengi
            state="disabled"  # Başlangıçta pasif
        )
        self.detect_btn.pack(side="left", padx=30)
        self.detect_btn.configure(cursor="@cat2.cur")

        # Sonuç listesi
        result_frame = ctk.CTkFrame(self.root, fg_color="#e2b4c1", border_width=2, border_color="#a55166")
        result_frame.pack(padx=20, pady=10, fill="x")
        
        self.result_text = ctk.CTkTextbox(
            result_frame,
            height=100,
            font=ctk.CTkFont(size=14),
            fg_color="#f7dae7",
            text_color="#a55166",
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
            self.detect_btn.configure(state="normal", cursor="@cat2.cur")
            
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
        results = self.model(self.image_path, conf = 0.15)
        
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