import os
import sys
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
from pptx import Presentation
from pptx.util import Inches

# Configure matplotlib for Times New Roman font style matching academic publications
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'font.size': 9,
    'axes.labelsize': 10,
    'axes.titlesize': 11,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'figure.dpi': 200
})

output_dir = r"C:\Users\Acer\.gemini\antigravity\scratch\HUST_HearingAid_Presentation"
os.makedirs(output_dir, exist_ok=True)

# -----------------------------------------------------------------------------
# 1. PARAMETERS & DSP DATA GENERATION
# -----------------------------------------------------------------------------
Fs = 48000          # Sampling frequency (48 kHz)
Fpass = 3000        # Passband cutoff (3 kHz)
N_order = 64        # Filter order

# Design filter
nyq = Fs / 2
h_ideal = signal.firwin(N_order + 1, Fpass / nyq, window='hamming')
h_quantized = np.round(h_ideal * 256) / 256  # POT 8-bit quantization

# Simulate time signals
t = np.arange(0, 0.015, 1/Fs) # 15 ms duration
signal_low = np.sin(2 * np.pi * 500 * t) # 500 Hz speech tone
noise_high = 0.4 * np.sin(2 * np.pi * 12000 * t) # 12 kHz noise
x_Left = signal_low + noise_high # Noisy input

# Filter using POT quantized filter
y_pot = signal.lfilter(h_quantized, 1, x_Left)

# Group delay compensation (N_order / 2) to align signals for perfect overlay
delay = int(N_order / 2)
t_aligned = t[delay:]
x_aligned = x_Left[:-delay]
y_aligned = y_pot[delay:]


# -----------------------------------------------------------------------------
# PLOT A: ADC CONVERSION (SLIDE 4)
# -----------------------------------------------------------------------------
plt.figure(figsize=(7, 3.8))
Fs_visual = 8000
Ts_visual = 1 / Fs_visual
t_analog = np.linspace(0, 0.003, 1000)
x_analog = np.sin(2 * np.pi * 1000 * t_analog)
t_sampled = np.arange(0, 0.003, Ts_visual)
x_sampled = np.sin(2 * np.pi * 1000 * t_sampled)
levels = 8
x_quantized = np.round((x_sampled + 1) / 2 * (levels - 1)) / (levels - 1) * 2 - 1

plt.plot(t_analog * 1000, x_analog, color='gray', linestyle='--', linewidth=1.5, label='Tín hiệu âm thanh tương tự - Analog x(t)')
markerline, stemlines, baseline = plt.stem(t_sampled * 1000, x_sampled, linefmt='red', markerfmt='ro', label='Lấy mẫu rời rạc (Sampling, Fs = 48 kHz)')
plt.setp(markerline, markersize=5)
plt.setp(stemlines, linewidth=1.0)
plt.setp(baseline, visible=False)
plt.step(t_sampled * 1000, x_quantized, where='mid', color='#0056b3', linewidth=1.8, label='Tín hiệu số hóa 16-bit (Quantized x(n))')

plt.title('Khâu chuyển đổi tương tự - số qua bộ ADC', fontsize=12, fontweight='bold', pad=10)
plt.xlabel('Thời gian (ms)', fontsize=10)
plt.ylabel('Biên độ', fontsize=10)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(loc='lower left', frameon=True, edgecolor='lightgray', facecolor='white', framealpha=0.9)
plt.ylim([-1.2, 1.2])
plt.xlim([0, 3.0])
plt.tight_layout()

adc_plot_path = os.path.join(output_dir, 'adc_conversion.png')
plt.savefig(adc_plot_path, dpi=250)
plt.close()
print("Generated ADC plot.")


# -----------------------------------------------------------------------------
# PLOT B: 6-STEP SIGNAL PROCESSING PIPELINE (SLIDE 5)
# -----------------------------------------------------------------------------
# Setup time axis for 6-step grid (6 ms window)
t_grid = np.arange(0, 0.006, 1/Fs)
f_sig = 500
f_noise = 12000

# 1. Acoustic Input
s1 = np.sin(2 * np.pi * f_sig * t_grid)
# 2. Microphone Output (Analog voltage with noise)
s2 = s1 + 0.4 * np.sin(2 * np.pi * f_noise * t_grid)
# 3. ADC Output (Digital sampled/quantized staircase of s2)
t_vis = np.arange(0, 0.006, 1/12000) # visual sample rate 12 kHz
s2_sampled = np.sin(2 * np.pi * f_sig * t_vis) + 0.4 * np.sin(2 * np.pi * f_noise * t_vis)
s3_quant = np.round((s2_sampled + 1.4)/2.8 * 7) / 7 * 2.8 - 1.4
# 4. DSP Output (Filtered digital staircase)
s4_quant = np.round((np.sin(2 * np.pi * f_sig * t_vis) + 1)/2 * 7) / 7 * 2 - 1
# 5. DAC Output (Analog clean reconstructed voltage)
s5 = np.sin(2 * np.pi * f_sig * t_grid)
# 6. Speaker Output (Acoustic amplified clean wave)
s6 = 1.5 * np.sin(2 * np.pi * f_sig * t_grid)

fig, axs = plt.subplots(3, 2, figsize=(8.5, 6))

# Panel 1: Step 1 Sound wave in (Analog)
axs[0, 0].plot(t_grid * 1000, s1, color='#0056b3', linewidth=1.5)
axs[0, 0].set_title('Bước 1: Sóng âm vào (Analog x(t))', fontweight='bold', fontsize=10)
axs[0, 0].set_xlim([0, 6.0])
axs[0, 0].set_ylim([-1.8, 1.8])
axs[0, 0].grid(True, linestyle='--', alpha=0.5)

# Panel 2: Step 2 Microphone Output (Noisy analog)
axs[0, 1].plot(t_grid * 1000, s2, color='#ff6b6b', linewidth=1.2)
axs[0, 1].set_title('Bước 2: Sau Microphone (Lẫn nhiễu)', fontweight='bold', fontsize=10)
axs[0, 1].set_xlim([0, 6.0])
axs[0, 1].set_ylim([-1.8, 1.8])
axs[0, 1].grid(True, linestyle='--', alpha=0.5)

# Panel 3: Step 3 ADC Output (Staircase noisy digital)
axs[1, 0].step(t_vis * 1000, s3_quant, where='mid', color='#ff6b6b', linewidth=1.5)
axs[1, 0].set_title('Bước 3: Sau bộ ADC (Số hóa x(n))', fontweight='bold', fontsize=10)
axs[1, 0].set_xlim([0, 6.0])
axs[1, 0].set_ylim([-1.8, 1.8])
axs[1, 0].grid(True, linestyle='--', alpha=0.5)

# Panel 4: Step 4 DSP Filter Output (Staircase clean digital)
axs[1, 1].step(t_vis * 1000, s4_quant, where='mid', color='#0056b3', linewidth=1.5)
axs[1, 1].set_title('Bước 4: Bộ xử lý MSDAP (Thuật toán POT)', fontweight='bold', fontsize=10)
axs[1, 1].set_xlim([0, 6.0])
axs[1, 1].set_ylim([-1.8, 1.8])
axs[1, 1].grid(True, linestyle='--', alpha=0.5)

# Panel 5: Step 5 DAC Output (Reconstructed clean analog voltage)
axs[2, 0].plot(t_grid * 1000, s5, color='#0056b3', linewidth=1.5)
axs[2, 0].set_title('Bước 5: Sau bộ DAC (Khôi phục)', fontweight='bold', fontsize=10)
axs[2, 0].set_xlabel('Thời gian (ms)', fontsize=9)
axs[2, 0].set_xlim([0, 6.0])
axs[2, 0].set_ylim([-1.8, 1.8])
axs[2, 0].grid(True, linestyle='--', alpha=0.5)

# Panel 6: Step 6 Receiver Output (Amplified clean sound)
axs[2, 1].plot(t_grid * 1000, s6, color='#2ca02c', linewidth=1.8)
axs[2, 1].set_title('Bước 6: Ngõ ra Loa (Khuếch đại)', fontweight='bold', fontsize=10)
axs[2, 1].set_xlabel('Thời gian (ms)', fontsize=9)
axs[2, 1].set_xlim([0, 6.0])
axs[2, 1].set_ylim([-1.8, 1.8])
axs[2, 1].grid(True, linestyle='--', alpha=0.5)

# Add y labels
for ax in axs[:, 0]:
    ax.set_ylabel('Biên độ', fontsize=9)

plt.suptitle('DẠNG SÓNG TÍN HIỆU BIẾN ĐỔI QUA 6 BƯỚC XỬ LÝ', fontsize=12, fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.96])

pipeline_plot_path = os.path.join(output_dir, 'pipeline_6steps.png')
plt.savefig(pipeline_plot_path, dpi=250)
plt.close()
print("Generated 6-step pipeline plot.")


# -----------------------------------------------------------------------------
# PLOT C: FREQUENCY SPECTRUM (SLIDE 10)
# -----------------------------------------------------------------------------
plt.figure(figsize=(7, 3.8))
n_fft = 4096
freqs = np.fft.rfftfreq(n_fft, d=1/Fs)
fft_in = np.abs(np.fft.rfft(x_Left, n=n_fft)) / (len(x_Left)/2)
fft_out = np.abs(np.fft.rfft(y_pot, n=n_fft)) / (len(y_pot)/2)
fft_in_norm = fft_in / np.max(fft_in)
fft_out_norm = fft_out / np.max(fft_in)

plt.plot(freqs, fft_in_norm, color='#ff6b6b', linewidth=1.0, label='Phổ tín hiệu thô (Cọc nhiễu 12 kHz rất cao)')
plt.plot(freqs, fft_out_norm, color='#0056b3', linewidth=1.8, label='Phổ tín hiệu sau lọc (Cọc 12 kHz bị triệt tiêu)')
plt.title('Đánh giá đáp ứng tần số qua phổ FFT', fontsize=12, fontweight='bold', pad=10)
plt.xlabel('Tần số (Hz)', fontsize=10)
plt.ylabel('Năng lượng', fontsize=10)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(loc='upper right', frameon=True, edgecolor='lightgray')
plt.xlim([0, 16000])
plt.ylim([-0.05, 1.1])
plt.tight_layout()

fft_plot_path = os.path.join(output_dir, 'fft_domain_matching.png')
plt.savefig(fft_plot_path, dpi=250)
plt.close()
print("Generated frequency domain plot.")


# -----------------------------------------------------------------------------
# PLOT D: TIME DOMAIN MATCHING (SLIDE 11)
# -----------------------------------------------------------------------------
plt.figure(figsize=(7, 3.8))
plt.plot(t_aligned, x_aligned, color='#ff6b6b', linewidth=1.0, label='Tín hiệu thô (Lẫn nhiễu cao tần 12 kHz)')
plt.plot(t_aligned, y_aligned, color='#0056b3', linewidth=1.8, label='Tín hiệu sau lọc POT (Sạch nhiễu)')
plt.title('So sánh tín hiệu âm thanh trên miền thời gian', fontsize=12, fontweight='bold', pad=10)
plt.xlabel('Thời gian (s)', fontsize=10)
plt.ylabel('Biên độ', fontsize=10)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(loc='upper right', frameon=True, edgecolor='lightgray')
plt.xlim([t_aligned[0], t_aligned[-1]])
plt.tight_layout()

time_plot_path = os.path.join(output_dir, 'time_domain_matching.png')
plt.savefig(time_plot_path, dpi=250)
plt.close()
print("Generated time domain plot.")


# -----------------------------------------------------------------------------
# 3. EMBED IMAGES INTO POWERPOINT PRESENTATION VERSION 3
# -----------------------------------------------------------------------------
pptx_path = os.path.join(output_dir, "HUST_BTL_TinHieuHeThong_HearingAid_v3.pptx")
print(f"Loading presentation v3 to embed all plots: {pptx_path}...")
prs = Presentation(pptx_path)

slide_adc = None      # Slide 4
slide_pipe = None     # Slide 5
slide_freq = None     # Slide 10
slide_time = None     # Slide 11

for idx, slide in enumerate(prs.slides):
    title_text = ""
    if slide.shapes.title:
        title_text = slide.shapes.title.text.lower()
    
    layout_name = slide.slide_layout.name.lower()
    safe_title = title_text.encode('ascii', 'replace').decode('ascii')
    print(f"Slide {idx+1} (Layout: {layout_name}) Title: '{safe_title}'")
    
    if "two content" in layout_name:
        if "số hóa" in title_text or "so hoa" in title_text:
            slide_adc = slide
            print(f"-> Mapped Slide {idx+1} as target ADC slide!")
        elif "6 bước" in title_text or "6 buoc" in title_text or "quy trình" in title_text or "quy trinh" in title_text:
            slide_pipe = slide
            print(f"-> Mapped Slide {idx+1} as target Pipeline slide!")
        elif "tần số" in title_text or "tan so" in title_text or "đáp ứng tần số" in title_text:
            slide_freq = slide
            print(f"-> Mapped Slide {idx+1} as target FFT slide!")
        elif "thời gian" in title_text or "thoi gian" in title_text:
            slide_time = slide
            print(f"-> Mapped Slide {idx+1} as target Time-Domain slide!")

# Function to replace placeholder index 2 (right column) with image
def replace_right_column_with_image(slide, image_path, custom_aspect_ratio=None):
    if not slide:
        print("ERROR: Target slide not assigned!")
        return
        
    target_placeholder = None
    for shape in slide.shapes:
        if shape.is_placeholder and shape.placeholder_format.idx == 2:
            target_placeholder = shape
            break
            
    if not target_placeholder:
        placeholders = [s for s in slide.shapes if s.is_placeholder]
        if len(placeholders) > 2:
            target_placeholder = placeholders[2]

    if target_placeholder:
        left = target_placeholder.left
        top = target_placeholder.top
        width = target_placeholder.width
        height = target_placeholder.height
        
        # Determine aspect ratio (width / height)
        # Default generated plots are 7:3.8 (1.84)
        # Pipeline plot is 8.5:6 (1.41)
        r_w, r_h = (8.5, 6.0) if custom_aspect_ratio == "pipe" else (7.0, 3.8)
        
        adjusted_height = int(width * (r_h / r_w))
        if adjusted_height > height:
            adjusted_height = height
            width = int(height * (r_w / r_h))
            
        top_offset = top + (height - adjusted_height) // 2
        
        # Remove placeholder shape
        sp = target_placeholder._element
        sp.getparent().remove(sp)
        
        # Insert picture
        slide.shapes.add_picture(image_path, left, top_offset, width, adjusted_height)
        print(f"Successfully inserted {os.path.basename(image_path)} in slide.")
    else:
        print(f"ERROR: Right placeholder not found in slide!")

# Embed into each slide
print("\nEmbedding plots...")
replace_right_column_with_image(slide_adc, adc_plot_path)
replace_right_column_with_image(slide_pipe, pipeline_plot_path, custom_aspect_ratio="pipe")
replace_right_column_with_image(slide_freq, fft_plot_path)
replace_right_column_with_image(slide_time, time_plot_path)

# Save
prs.save(pptx_path)
print(f"\nSUCCESS: Successfully saved presentation v3 with ALL 4 embedded plots at: {pptx_path}")
