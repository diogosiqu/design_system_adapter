import cv2
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
import colorsys

class DesignSystemAdapter:
    def __init__(self, logo_path):
        self.logo_path = logo_path
        self.logo_image = self.load_image()
        self.dominant_colors = []
        self.color_palette = {}
        
    def load_image(self):
        """Carrega a imagem do logotipo"""
        image = cv2.imread(self.logo_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image
    
    def extract_dominant_colors(self, n_colors=5):
        """Extrai as cores dominantes da imagem"""
        # Redimensionar para melhorar performance
        resized_image = cv2.resize(self.logo_image, (100, 100))
        
        # Reformatar para análise
        pixels = resized_image.reshape(-1, 3)
        
        # Aplicar K-means
        kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
        kmeans.fit(pixels)
        
        # Obter as cores dominantes e suas frequências
        colors = kmeans.cluster_centers_
        labels = kmeans.labels_
        counts = np.bincount(labels)
        
        # Ordenar por frequência
        colors_with_counts = [(color, count) for color, count in zip(colors, counts)]
        colors_with_counts.sort(key=lambda x: x[1], reverse=True)
        
        # Armazenar cores dominantes como RGB inteiros
        self.dominant_colors = [color.astype(int) for color, _ in colors_with_counts]
        return self.dominant_colors
    
    def generate_color_palette(self):
        """Gera uma paleta de cores completa a partir das cores dominantes"""
        if not self.dominant_colors:
            self.extract_dominant_colors()
        
        # A cor mais frequente será a primária
        primary_color = self.dominant_colors[0]
        
        # Converter para HSV para manipulação
        h, s, v = colorsys.rgb_to_hsv(primary_color[0]/255, primary_color[1]/255, primary_color[2]/255)
        
        # Gerar cores complementares
        complementary_h = (h + 0.5) % 1.0
        complementary_rgb = colorsys.hsv_to_rgb(complementary_h, s, v)
        complementary_color = [int(c * 255) for c in complementary_rgb]
        
        # Gerar variações da cor primária (mais escura e mais clara)
        darker_primary = self._adjust_brightness(primary_color, -0.3)
        lighter_primary = self._adjust_brightness(primary_color, 0.3)
        
        # Gerar uma cor de acento (90 graus no círculo cromático)
        accent_h = (h + 0.25) % 1.0
        accent_rgb = colorsys.hsv_to_rgb(accent_h, s, v)
        accent_color = [int(c * 255) for c in accent_rgb]
        
        # Gerar cinzas para texto e backgrounds
        light_gray = [240, 240, 240]
        medium_gray = [150, 150, 150]
        dark_gray = [50, 50, 50]
        
        # Armazenar a paleta completa
        self.color_palette = {
            "primary": self._rgb_to_hex(primary_color),
            "primary-dark": self._rgb_to_hex(darker_primary),
            "primary-light": self._rgb_to_hex(lighter_primary),
            "secondary": self._rgb_to_hex(complementary_color),
            "accent": self._rgb_to_hex(accent_color),
            "gray-light": self._rgb_to_hex(light_gray),
            "gray-medium": self._rgb_to_hex(medium_gray),
            "gray-dark": self._rgb_to_hex(dark_gray)
        }
        
        # Se temos mais cores dominantes, vamos usá-las como cores adicionais
        if len(self.dominant_colors) > 1:
            for i, color in enumerate(self.dominant_colors[1:4], 1):  # Limitamos a 3 cores adicionais
                self.color_palette[f"additional-{i}"] = self._rgb_to_hex(color)
        
        return self.color_palette
    
    def _adjust_brightness(self, rgb_color, factor):
        """Ajusta o brilho de uma cor RGB"""
        h, s, v = colorsys.rgb_to_hsv(rgb_color[0]/255, rgb_color[1]/255, rgb_color[2]/255)
        v = max(0, min(1, v + factor))
        rgb = colorsys.hsv_to_rgb(h, s, v)
        return [int(c * 255) for c in rgb]
    
    def _rgb_to_hex(self, rgb_color):
        """Converte uma cor RGB para formato hexadecimal"""
        return f"#{int(rgb_color[0]):02x}{int(rgb_color[1]):02x}{int(rgb_color[2]):02x}"
    
    def generate_scss_variables(self):
        """Gera variáveis SCSS a partir da paleta de cores"""
        if not self.color_palette:
            self.generate_color_palette()
        
        scss_content = "// Design System Auto-Adaptativo - Cores geradas automaticamente\n\n"
        
        # Adicionar variáveis de cores
        for color_name, color_value in self.color_palette.items():
            scss_content += f"$color-{color_name}: {color_value};\n"
        
        return scss_content
    
    def export_scss_file(self, output_path="colors.scss"):
        """Exporta as variáveis SCSS para um arquivo"""
        scss_content = self.generate_scss_variables()
        
        with open(output_path, "w") as f:
            f.write(scss_content)
        
        print(f"Arquivo SCSS exportado com sucesso para {output_path}")
    
    def visualize_palette(self):
        """Visualiza a paleta de cores gerada"""
        if not self.color_palette:
            self.generate_color_palette()
        
        # Preparar cores para visualização
        colors = list(self.color_palette.values())
        labels = list(self.color_palette.keys())
        
        # Criar gráfico
        plt.figure(figsize=(12, 5))
        for i, (color, label) in enumerate(zip(colors, labels)):
            plt.bar(i, 1, color=color, width=0.7)
            plt.text(i, 0.5, label, ha='center', rotation=90, color='white' if sum([int(color[j:j+2], 16) for j in (1, 3, 5)]) < 380 else 'black')
        
        plt.title('Paleta de Cores Gerada')
        plt.xlim(-0.5, len(colors) - 0.5)
        plt.ylim(0, 1)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig('palette_preview.png')
        plt.close()
        
        print("Visualização da paleta salva como 'palette_preview.png'")
        
    def analyze_contrast(self):
        """Analisa o contraste entre cores primárias e de texto para verificar acessibilidade"""
        if not self.color_palette:
            self.generate_color_palette()
            
        # Função para calcular contraste (fórmula WCAG)
        def calculate_contrast(color1_hex, color2_hex):
            def get_luminance(hex_color):
                r, g, b = int(hex_color[1:3], 16)/255, int(hex_color[3:5], 16)/255, int(hex_color[5:7], 16)/255
                r = r/12.92 if r <= 0.03928 else ((r+0.055)/1.055) ** 2.4
                g = g/12.92 if g <= 0.03928 else ((g+0.055)/1.055) ** 2.4
                b = b/12.92 if b <= 0.03928 else ((b+0.055)/1.055) ** 2.4
                return 0.2126 * r + 0.7152 * g + 0.0722 * b
            
            l1 = get_luminance(color1_hex)
            l2 = get_luminance(color2_hex)
            
            if l1 > l2:
                return (l1 + 0.05) / (l2 + 0.05)
            else:
                return (l2 + 0.05) / (l1 + 0.05)
        
        # Verificar contraste
        contrast_results = {}
        text_colors = [self.color_palette["gray-light"], self.color_palette["gray-dark"]]
        background_colors = [self.color_palette["primary"], self.color_palette["secondary"], 
                             self.color_palette["primary-light"], self.color_palette["primary-dark"]]
        
        for text_color in text_colors:
            text_name = "texto-claro" if text_color == self.color_palette["gray-light"] else "texto-escuro"
            for bg_color in background_colors:
                bg_name = [k for k, v in self.color_palette.items() if v == bg_color][0]
                contrast = calculate_contrast(text_color, bg_color)
                
                if contrast >= 4.5:
                    status = "Bom" if contrast >= 7 else "Aceitável"
                else:
                    status = "Insuficiente"
                
                contrast_results[f"{text_name} sobre {bg_name}"] = {
                    "contraste": round(contrast, 2),
                    "status": status
                }
        
        return contrast_results

# Exemplo de uso
if __name__ == "__main__":
    adapter = DesignSystemAdapter("logo.png")
    adapter.extract_dominant_colors(n_colors=6)
    adapter.generate_color_palette()
    adapter.export_scss_file("theme-colors.scss")
    adapter.visualize_palette()
    
    # Analisar contraste para acessibilidade
    contrast_results = adapter.analyze_contrast()
    print("\nAnálise de Contraste para Acessibilidade:")
    for combination, result in contrast_results.items():
        print(f"{combination}: {result['contraste']} - {result['status']}")