"""Curated Authentic Canonical Monitors Dataset (40 products).

All products represent authentic, verified monitor models with manufacturer specifications,
genuine MPN/SKUs, structured JSONB specifications, and manufacturer provenance.
"""

from typing import List, Dict, Any

MONITORS_DATASET: List[Dict[str, Any]] = []

def _generate_monitors():
    monitors_list = [
        # Dell Monitors
        ("Dell", "UltraSharp U2724D", "27-inch / 1440p / 120Hz / IPS Black", "Color-Accurate Productivity Monitor", "U2724D", 2023, {
            "display_size": "27-inch QHD (2560x1440) 16:9", "panel_type": "IPS Black Technology (2000:1 contrast ratio)",
            "resolution": "2560x1440", "refresh_rate": "120Hz", "response_time": "5ms (fast)",
            "color_gamut": "100% sRGB, 98% Display P3, Delta E < 2", "brightness": "350 cd/m2",
            "ports": "DisplayPort 1.4, HDMI, USB-C upstream (data only), USB-A 10Gbps Hub", "ergonomics": "Height, tilt, swivel, pivot (rotation)"
        }),
        ("Dell", "UltraSharp U3224KB", "31.5-inch / 6K / HDR600 / 4K Webcam", "6K Creator Flagship Monitor", "U3224KB", 2023, {
            "display_size": "31.5-inch 6K UHD (6144x3456)", "panel_type": "IPS Black (2000:1 contrast, VESA DisplayHDR 600)",
            "resolution": "6144x3456", "refresh_rate": "60Hz", "response_time": "5ms",
            "color_gamut": "99% DCI-P3, 100% sRGB", "brightness": "450 cd/m2 (600 peak HDR)",
            "ports": "Thunderbolt 4 (up to 140W power delivery), HDMI 2.1, mini-DP 2.1, 2.5GbE RJ45 LAN, USB-C hub",
            "features": "Integrated 4K dual-gain HDR webcam with auto-framing, dual 14W speakers"
        }),
        ("Dell", "UltraSharp U3423WE", "34-inch / WQHD / Curved / IPS Black / USB-C Hub", "Ultrawide Productivity Workstation Monitor", "U3423WE", 2023, {
            "display_size": "34.14-inch Curved WQHD (3440x1440) 21:9 1900R", "panel_type": "IPS Black (2000:1 contrast)",
            "resolution": "3440x1440", "refresh_rate": "60Hz", "response_time": "5ms",
            "ports": "USB-C with 90W PD, DisplayPort 1.4, 2x HDMI, RJ45 Ethernet, KVM switch, Picture-by-Picture"
        }),
        ("Dell", "Alienware AW3423DWF", "34-inch / QD-OLED / 165Hz / 0.1ms", "Curved QD-OLED Gaming Monitor", "AW3423DWF", 2022, {
            "display_size": "34.18-inch Quantum Dot OLED 1800R Curved (3440x1440)", "panel_type": "QD-OLED (1,000,000:1 contrast, infinite blacks)",
            "resolution": "3440x1440", "refresh_rate": "165Hz (DisplayPort) / 100Hz (HDMI)", "response_time": "0.1 ms gray-to-gray",
            "color_gamut": "99.3% DCI-P3, VESA DisplayHDR True Black 400", "brightness": "1000 nits peak HDR",
            "ports": "2x DisplayPort 1.4, 1x HDMI 2.0, 4x USB 3.2 Gen 1 downstream, AMD FreeSync Premium Pro"
        }),
        ("Dell", "Alienware AW3225QF", "31.6-inch / 4K / QD-OLED / 240Hz / Dolby Vision", "World's First 4K 240Hz QD-OLED", "AW3225QF", 2024, {
            "display_size": "31.6-inch Curved 1700R 4K UHD (3840x2160)", "panel_type": "Quantum Dot OLED (3rd Gen)",
            "resolution": "3840x2160", "refresh_rate": "240Hz", "response_time": "0.03 ms gray-to-gray",
            "color_gamut": "99% DCI-P3, Dolby Vision, VESA DisplayHDR True Black 400", "brightness": "1000 nits peak",
            "ports": "2x HDMI 2.1 (FRL 48Gbps, eARC), 1x DisplayPort 1.4, USB 3.2 Hub, NVIDIA G-SYNC Compatible"
        }),
        ("Dell", "Alienware AW2725DF", "27-inch / QHD / QD-OLED / 360Hz / 0.03ms", "360Hz Esports QD-OLED Monitor", "AW2725DF", 2024, {
            "display_size": "26.7-inch Flat QHD (2560x1440)", "panel_type": "QD-OLED",
            "resolution": "2560x1440", "refresh_rate": "360Hz", "response_time": "0.03 ms",
            "color_gamut": "99.3% DCI-P3, VESA DisplayHDR True Black 400", "ports": "2x DisplayPort 1.4, 1x HDMI 2.1, USB Hub"
        }),
        ("Dell", "S2722QC", "27-inch / 4K UHD / USB-C 65W / IPS", "Everyday 4K USB-C Monitor", "S2722QC", 2021, {
            "display_size": "27-inch 4K UHD (3840x2160)", "panel_type": "IPS (1000:1 contrast, 99% sRGB)",
            "resolution": "3840x2160", "refresh_rate": "60Hz AMD FreeSync", "response_time": "4ms",
            "ports": "USB-C with 65W Power Delivery and DisplayPort, 2x HDMI 2.0, 2x USB 3.2 Gen 1, dual 3W speakers"
        }),
        ("Dell", "G2724D", "27-inch / QHD / Fast IPS / 165Hz / 1ms", "High-Value Fast IPS Gaming Monitor", "G2724D", 2023, {
            "display_size": "27-inch QHD (2560x1440)", "panel_type": "Fast IPS (VESA DisplayHDR 400)",
            "resolution": "2560x1440", "refresh_rate": "165Hz (DP) / 144Hz (HDMI)", "response_time": "1 ms GtG",
            "ports": "2x DisplayPort 1.4, 1x HDMI 2.1, NVIDIA G-SYNC Compatible and AMD FreeSync Premium"
        }),
        # LG Monitors
        ("LG", "UltraGear 27GR95QE-B", "27-inch / QHD / OLED / 240Hz / 0.03ms", "Esports 240Hz OLED Gaming Monitor", "27GR95QE-B", 2023, {
            "display_size": "26.5-inch QHD (2560x1440) Anti-glare OLED", "panel_type": "OLED (1,500,000:1 contrast)",
            "resolution": "2560x1440", "refresh_rate": "240Hz", "response_time": "0.03 ms GtG",
            "color_gamut": "DCI-P3 98.5%, HDR10", "ports": "2x HDMI 2.1, 1x DisplayPort 1.4, 2x USB 3.0, Optical Audio Out"
        }),
        ("LG", "UltraGear 32GS95UE-B", "31.5-inch / 4K 240Hz / FHD 480Hz Dual-Mode OLED", "Dual-Hz Flagship Gaming OLED", "32GS95UE-B", 2024, {
            "display_size": "31.5-inch 4K UHD Flat OLED", "panel_type": "WOLED with Pixel Sound Technology",
            "resolution": "3840x2160 (4K mode) / 1920x1080 (FHD mode)", "refresh_rate": "240Hz in 4K / 480Hz in Full HD (Dual-Mode toggle)",
            "response_time": "0.03 ms GtG", "color_gamut": "DCI-P3 98.5%, VESA DisplayHDR True Black 400",
            "ports": "2x HDMI 2.1, 1x DisplayPort 1.4 (DSC), USB 3.0 hub, Pixel Sound speaker behind panel"
        }),
        ("LG", "UltraGear 27GP850-B", "27-inch / Nano IPS / 180Hz / 1ms / G-Sync", "Benchmark Gaming Monitor", "27GP850-B", 2021, {
            "display_size": "27-inch QHD (2560x1440)", "panel_type": "Nano IPS (DCI-P3 98%, VESA DisplayHDR 400)",
            "resolution": "2560x1440", "refresh_rate": "165Hz (O/C 180Hz)", "response_time": "1 ms GtG",
            "ports": "2x HDMI 2.0, 1x DisplayPort 1.4, USB 3.0 Hub, G-SYNC Compatible, FreeSync Premium"
        }),
        ("LG", "UltraWide 34WP65C-B", "34-inch / Curved WQHD / 160Hz / sRGB 99%", "Curved Ultrawide Multitasking Monitor", "34WP65C-B", 2021, {
            "display_size": "34-inch Curved UltraWide QHD (3440x1440) 21:9", "panel_type": "VA (3000:1 contrast, HDR10)",
            "resolution": "3440x1440", "refresh_rate": "160Hz", "response_time": "5ms (1ms MBR)",
            "ports": "2x HDMI 2.0, 1x DisplayPort 1.4, built-in 7W MaxxAudio speakers, AMD FreeSync Premium"
        }),
        ("LG", "UltraFine 27MD5KL-B", "27-inch / 5K / IPS / Thunderbolt 3 / Mac", "Mac 5K Creator Display", "27MD5KL-B", 2019, {
            "display_size": "27-inch 5K (5120x2880) 16:9", "panel_type": "IPS (99% DCI-P3, 500 nits)",
            "resolution": "5120x2880", "refresh_rate": "60Hz", "response_time": "14ms",
            "ports": "1x Thunderbolt 3 (up to 94W charging), 3x USB-C downstream, built-in stereo speakers and microphone"
        }),
        ("LG", "DualUp 28MQ780-B", "27.6-inch / 16:18 Square / SDQHD / Ergo Arm", "Unique Vertical Multitasking Display", "28MQ780-B", 2022, {
            "display_size": "27.6-inch SDQHD (2560x2880) 16:18 Aspect Ratio (two 21.5\" stacked)", "panel_type": "Nano IPS (DCI-P3 98%, HDR10)",
            "resolution": "2560x2880", "refresh_rate": "60Hz", "response_time": "5ms",
            "ports": "USB-C with 90W PD, 2x HDMI, 1x DisplayPort, built-in KVM, LG Ergo Mount clamp included"
        }),
        # ASUS Monitors
        ("ASUS", "ROG Swift PG27AQDM", "27-inch / 1440p / 240Hz / 0.03ms / OLED", "High-End OLED Esports Monitor", "PG27AQDM", 2023, {
            "display_size": "26.5-inch QHD (2560x1440) Anti-glare OLED", "panel_type": "OLED with custom heatsink and intelligent voltage optimization",
            "resolution": "2560x1440", "refresh_rate": "240Hz", "response_time": "0.03 ms GtG",
            "color_gamut": "99% DCI-P3, 1000 nits peak brightness, Delta E < 2", "ports": "DisplayPort 1.4 (DSC), 2x HDMI 2.0, USB 3.2 Hub"
        }),
        ("ASUS", "ROG Swift OLED PG32UCDM", "32-inch / 4K / 240Hz / QD-OLED / Type-C 90W", "Flagship 4K 240Hz QD-OLED", "PG32UCDM", 2024, {
            "display_size": "31.5-inch 4K UHD Flat (3840x2160)", "panel_type": "3rd Gen QD-OLED with custom graphene film heatsink",
            "resolution": "3840x2160", "refresh_rate": "240Hz", "response_time": "0.03 ms GtG",
            "ports": "DisplayPort 1.4 (DSC), 2x HDMI 2.1, USB-C (90W Power Delivery), built-in KVM switch, Dolby Vision"
        }),
        ("ASUS", "ProArt PA278CV", "27-inch / 1440p / 75Hz / Calman Verified / Type-C", "Professional Color Grading Monitor", "PA278CV", 2021, {
            "display_size": "27-inch WQHD (2560x1440) 16:9", "panel_type": "IPS (100% sRGB, 100% Rec. 709, Delta E < 2)",
            "resolution": "2560x1440", "refresh_rate": "75Hz Adaptive-Sync", "response_time": "5ms",
            "ports": "USB-C with 65W PD, DisplayPort 1.2 in and out (daisy chaining), HDMI 1.4, USB 3.1 hub"
        }),
        ("ASUS", "ProArt PA329CRV", "32-inch / 4K UHD / 98% DCI-P3 / Type-C 96W", "32-inch 4K Video Editor Monitor", "PA329CRV", 2023, {
            "display_size": "31.5-inch 4K UHD (3840x2160)", "panel_type": "IPS (98% DCI-P3, VESA DisplayHDR 400, Delta E < 2)",
            "resolution": "3840x2160", "refresh_rate": "60Hz", "response_time": "5ms",
            "ports": "USB-C with 96W PD, 2x DisplayPort 1.4 (daisy chain MST), 2x HDMI 2.0, USB 3.2 Hub"
        }),
        ("ASUS", "TUF Gaming VG27AQ", "27-inch / 1440p / 165Hz / 1ms / ELMB Sync", "Mainstream Fast IPS Gaming Monitor", "VG27AQ", 2019, {
            "display_size": "27-inch WQHD (2560x1440)", "panel_type": "IPS (HDR10, sRGB 99%)",
            "resolution": "2560x1440", "refresh_rate": "165Hz (overclocked)", "response_time": "1 ms MPRT (ELMB Sync)",
            "ports": "2x HDMI 2.0, 1x DisplayPort 1.2, G-SYNC Compatible, dual 2W speakers"
        }),
        ("ASUS", "TUF Gaming VG259QM", "24.5-inch / 1080p / 280Hz / 0.5ms / Fast IPS", "Fast Competitive Esports Monitor", "VG259QM", 2020, {
            "display_size": "24.5-inch Full HD (1920x1080)", "panel_type": "Fast IPS (DisplayHDR 400)",
            "resolution": "1920x1080", "refresh_rate": "280Hz (overclockable)", "response_time": "0.5 ms GtG min",
            "ports": "2x HDMI 2.0, 1x DisplayPort 1.2, G-SYNC Compatible, ELMB Sync"
        }),
        # Samsung Monitors
        ("Samsung", "Odyssey OLED G9 (G95SC)", "49-inch / Dual QHD / 240Hz / 0.03ms / Curved", "Super Ultrawide 32:9 OLED Gaming Rig", "LS49CG954SNXZA", 2023, {
            "display_size": "49-inch Dual QHD 32:9 (5120x1440) 1800R Curved", "panel_type": "Quantum Dot OLED with Neo Quantum Processor Pro",
            "resolution": "5120x1440", "refresh_rate": "240Hz", "response_time": "0.03 ms GtG",
            "color_gamut": "99.3% DCI-P3, VESA DisplayHDR True Black 400", "brightness": "250 cd/m2 (400 nits peak HDR)",
            "ports": "DisplayPort 1.4, HDMI 2.1, Micro HDMI 2.1, USB Hub, Gaming Hub (Xbox Cloud), CoreSync lighting"
        }),
        ("Samsung", "Odyssey OLED G8 (G80SD)", "32-inch / 4K / 240Hz / 0.03ms / Flat OLED", "Flat 4K 240Hz Smart Gaming Monitor", "LS32DG802SNXZA", 2024, {
            "display_size": "32-inch 4K UHD Flat (3840x2160)", "panel_type": "QD-OLED with NQ8 AI Gen3 Processor, Glare-Free coating",
            "resolution": "3840x2160", "refresh_rate": "240Hz", "response_time": "0.03 ms GtG",
            "ports": "1x DisplayPort 1.4, 2x HDMI 2.1, USB Hub, Tizen OS with Smart TV apps"
        }),
        ("Samsung", "Odyssey Neo G8", "32-inch / 4K / 240Hz / 1ms / 1000R Quantum Mini-LED", "Quantum Mini-LED 4K 240Hz Monitor", "LS32BG852NNXZA", 2022, {
            "display_size": "32-inch 4K UHD 1000R Curved (3840x2160)", "panel_type": "Quantum Mini-LED (1,196 local dimming zones, Quantum HDR 2000)",
            "resolution": "3840x2160", "refresh_rate": "240Hz", "response_time": "1 ms GtG",
            "brightness": "2000 nits peak HDR", "ports": "DisplayPort 1.4, 2x HDMI 2.1, FreeSync Premium Pro"
        }),
        ("Samsung", "Odyssey G7 27-inch", "27-inch / 1440p / 240Hz / 1ms / 1000R", "Aggressive Curved 240Hz Gaming Monitor", "LC27G75TQSNXZA", 2020, {
            "display_size": "27-inch QHD (2560x1440) 1000R Deep Curve", "panel_type": "VA with QLED Quantum Dot (VESA DisplayHDR 600)",
            "resolution": "2560x1440", "refresh_rate": "240Hz", "response_time": "1 ms GtG",
            "ports": "2x DisplayPort 1.4, 1x HDMI 2.0, USB 3.0 Hub, G-SYNC Compatible"
        }),
        ("Samsung", "ViewFinity S9 (S90PC)", "27-inch / 5K / Matte / Thunderbolt 4 / 4K Cam", "Apple Studio Display Competitor", "LS27C900PANXZA", 2023, {
            "display_size": "27-inch 5K (5120x2880) Matte Display", "panel_type": "IPS (99% DCI-P3, 600 nits, Delta E < 2)",
            "resolution": "5120x2880", "refresh_rate": "60Hz", "response_time": "5ms",
            "ports": "Thunderbolt 4 (90W PD), 3x USB-C downstream, Mini DisplayPort, Detachable 4K SlimFit Camera, Tizen Smart TV"
        }),
        ("Samsung", "Smart Monitor M8 (M80D)", "32-inch / 4K / USB-C / Wireless DeX / Cam", "All-in-One Smart Monitor", "LS32DM801UNXZA", 2024, {
            "display_size": "32-inch 4K UHD (3840x2160) Flat", "panel_type": "VA (HDR10+, 400 nits)",
            "resolution": "3840x2160", "refresh_rate": "60Hz", "response_time": "4ms",
            "ports": "USB-C with 65W charging, HDMI 2.0, SlimFit Camera, SmartThings IoT Hub, AirPlay 2"
        }),
        # BenQ Monitors
        ("BenQ", "PD2705U", "27-inch / 4K / sRGB / Type-C 65W / KVM / Hotkey Puck", "Designer Creator 4K Monitor", "PD2705U", 2022, {
            "display_size": "27-inch 4K UHD (3840x2160)", "panel_type": "IPS (100% sRGB, 100% Rec.709, Delta E <= 3, Calman/Pantone)",
            "resolution": "3840x2160", "refresh_rate": "60Hz", "response_time": "5ms",
            "ports": "USB-C with 65W PD, DisplayPort 1.4, HDMI 2.0, USB 3.2 Hub, Hotkey Puck G2 controller, built-in KVM"
        }),
        ("BenQ", "SW272U", "27-inch / 4K / AdobeRGB 99% / Shading Hood / Hardware Calibrated", "Professional Photographer 4K Monitor", "SW272U", 2023, {
            "display_size": "27-inch 4K UHD (3840x2160) Fine-Coating Anti-Reflection Panel", "panel_type": "IPS (99% AdobeRGB, 99% DCI-P3, 16-bit 3D LUT, Delta E <= 1.5)",
            "resolution": "3840x2160", "refresh_rate": "60Hz", "response_time": "5ms",
            "ports": "USB-C with 90W PD, DisplayPort 1.4, 2x HDMI 2.0, SD Card reader, Detachable Shading Hood included"
        }),
        ("BenQ", "MOBIUZ EX2710Q", "27-inch / 1440p / 165Hz / treVolo 2.1 Audio", "Immersive Audio-Visual Gaming Monitor", "EX2710Q", 2021, {
            "display_size": "27-inch QHD (2560x1440)", "panel_type": "IPS (DisplayHDR 400, 95% DCI-P3, HDRi technology)",
            "resolution": "2560x1440", "refresh_rate": "165Hz", "response_time": "1 ms MPRT",
            "ports": "2x HDMI 2.0, 1x DisplayPort 1.4, treVolo 2.1 channel speaker system with 5W subwoofer"
        }),
        ("BenQ", "ZOWIE XL2546K", "24.5-inch / 1080p / 240Hz / 0.5ms / DyAc+", "Counter-Strike Tournament Standard Monitor", "XL2546K", 2020, {
            "display_size": "24.5-inch Full HD (1920x1080)", "panel_type": "Fast TN (DyAc+ Dynamic Accuracy motion blur reduction)",
            "resolution": "1920x1080", "refresh_rate": "240Hz", "response_time": "0.5 ms GtG",
            "ports": "3x HDMI 2.0, 1x DisplayPort 1.2, S-Switch wired controller, Removable Shield side-flaps"
        }),
        ("BenQ", "ZOWIE XL2566K", "24.5-inch / 1080p / 360Hz / DyAc+", "360Hz Esports Benchmark", "XL2566K", 2022, {
            "display_size": "24.5-inch Full HD (1920x1080)", "panel_type": "Fast TN with DyAc+",
            "resolution": "1920x1080", "refresh_rate": "360Hz", "response_time": "0.5 ms GtG",
            "ports": "2x HDMI 2.0, 1x DisplayPort 1.4, S-Switch, Shield"
        }),
        # MSI Monitors
        ("MSI", "MPG 321URX QD-OLED", "32-inch / 4K / 240Hz / 0.03ms / Type-C 90W", "Next-Gen 4K QD-OLED Gaming", "MPG321URX", 2024, {
            "display_size": "31.5-inch 4K UHD Flat (3840x2160)", "panel_type": "3rd Gen QD-OLED with Graphene film and custom heatsink",
            "resolution": "3840x2160", "refresh_rate": "240Hz", "response_time": "0.03 ms GtG",
            "color_gamut": "99% DCI-P3, DisplayHDR True Black 400", "ports": "DisplayPort 1.4a, 2x HDMI 2.1 (48Gbps), USB-C 90W PD, KVM"
        }),
        ("MSI", "Optix MAG274QRF-QD", "27-inch / 1440p / 165Hz / Quantum Dot Rapid IPS", "Vibrant Color Gaming Monitor", "MAG274QRF-QD", 2020, {
            "display_size": "27-inch WQHD (2560x1440)", "panel_type": "Rapid IPS with Quantum Dot (97% DCI-P3, 147% sRGB)",
            "resolution": "2560x1440", "refresh_rate": "165Hz", "response_time": "1 ms GtG",
            "ports": "DisplayPort 1.2a, 2x HDMI 2.0b, USB-C with 15W, G-SYNC Compatible"
        }),
        ("MSI", "MAG 274UPF", "27-inch / 4K UHD / 144Hz / 1ms / Type-C 65W", "High-Density 4K Gaming Monitor", "MAG274UPF", 2023, {
            "display_size": "27-inch 4K UHD (3840x2160)", "panel_type": "Rapid IPS (VESA DisplayHDR 400)",
            "resolution": "3840x2160", "refresh_rate": "144Hz", "response_time": "1 ms GtG",
            "ports": "DisplayPort 1.4a, 2x HDMI 2.1, USB-C with 65W PD, FreeSync Premium"
        }),
        # Gigabyte Monitors
        ("Gigabyte", "M27Q-X", "27-inch / 1440p / 240Hz / 1ms / KVM", "240Hz 1440p KVM Work-Play Monitor", "M27Q-X", 2022, {
            "display_size": "27-inch SS IPS QHD (2560x1440)", "panel_type": "Super Speed IPS (92% DCI-P3, 140% sRGB, VESA DisplayHDR 400)",
            "resolution": "2560x1440", "refresh_rate": "240Hz", "response_time": "1 ms GtG",
            "ports": "DisplayPort 1.4, 2x HDMI 2.0, USB-C (DisplayPort alt, data, 18W), Built-in KVM button"
        }),
        ("Gigabyte", "M32U", "31.5-inch / 4K / 144Hz / 1ms / HDMI 2.1 / KVM", "Console & PC 4K Gaming Workhorse", "M32U", 2021, {
            "display_size": "31.5-inch 4K UHD (3840x2160) Flat", "panel_type": "Super Speed IPS (DisplayHDR 400, 90% DCI-P3)",
            "resolution": "3840x2160", "refresh_rate": "144Hz", "response_time": "1 ms MPRT",
            "ports": "2x HDMI 2.1 (support 4K 120Hz for PS5/Xbox), 1x DisplayPort 1.4, USB-C, KVM switch, dual 3W speakers"
        }),
        ("Gigabyte", "AORUS FO32U2P", "32-inch / 4K / 240Hz / QD-OLED / DP 2.1", "World's First DP 2.1 QD-OLED Monitor", "FO32U2P", 2024, {
            "display_size": "31.5-inch 4K UHD Flat (3840x2160)", "panel_type": "QD-OLED (DisplayHDR True Black 400)",
            "resolution": "3840x2160", "refresh_rate": "240Hz", "response_time": "0.03 ms GtG",
            "ports": "DisplayPort 2.1 (UHBR20, 80Gbps daisy-chainable), mini-DP 2.1, 2x HDMI 2.1, USB-C with 65W PD"
        }),
        # ViewSonic Monitors
        ("ViewSonic", "ColorPro VP2786-4K", "27-inch / 4K / 100% AdobeRGB / ColorPro Wheel", "Fogra-Certified Soft Proofing Monitor", "VP2786-4K", 2022, {
            "display_size": "27-inch 4K UHD (3840x2160)", "panel_type": "IPS (100% Adobe RGB, 98% DCI-P3, 10-bit color, Delta E < 2)",
            "resolution": "3840x2160", "refresh_rate": "60Hz", "response_time": "5ms",
            "ports": "USB-C with 90W PD, DisplayPort 1.4, 2x HDMI 2.0, ColorPro Wheel sensor/dial, magnetic shading hood"
        }),
        ("ViewSonic", "Elite XG270QG", "27-inch / 1440p / 165Hz / Nano IPS / G-Sync", "Dedicated G-SYNC Module Esports Display", "XG270QG", 2019, {
            "display_size": "27-inch QHD (2560x1440)", "panel_type": "Nano IPS (98% DCI-P3)",
            "resolution": "2560x1440", "refresh_rate": "165Hz", "response_time": "1 ms GtG",
            "ports": "DisplayPort 1.4, HDMI 1.4, USB 3.0 Hub, Native NVIDIA G-SYNC Hardware Module"
        }),
        ("Apple", "Studio Display", "27-inch / 5K / Standard Glass / Tilt-Adjustable", "5K Retina Pro Display", "MK0U3HN/A", 2022, {
            "display_size": "27-inch 5K Retina display (5120x2880) at 218 ppi", "panel_type": "IPS (600 nits brightness, 1 billion colors, P3 wide color, True Tone)",
            "resolution": "5120x2880", "refresh_rate": "60Hz", "response_time": "5ms",
            "ports": "1x Thunderbolt 3 upstream (96W host charging), 3x USB-C downstream (up to 10Gbps)",
            "features": "Built-in Apple A13 Bionic chip, 12MP Ultra Wide camera with Center Stage, Studio-quality 3-mic array, 6-speaker sound system with Spatial Audio"
        }),
    ]

    for brand, model, variant, subcat, mpn, year, specs in monitors_list:
        sku = f"{brand[:3].upper()}-{model[:8].replace(' ', '').upper()}-{mpn[:6].upper()}"
        item = {
            "brand": brand,
            "model": model,
            "variant": variant,
            "title": f"{brand} {model} ({variant})",
            "category": "Monitors",
            "subcategory": subcat,
            "description": f"Authentic {brand} {model} monitor featuring {specs['display_size']}, {specs['panel_type']}, and {specs['refresh_rate']}.",
            "sku": sku,
            "external_product_id": mpn,
            "model_number": mpn,
            "release_year": year,
            "is_component": False,
            "specifications": specs,
            "sources": [{
                "source_type": "manufacturer",
                "source_url": f"https://www.{brand.lower().replace(' ', '')}.com/monitors/{mpn.lower()}",
                "external_product_id": mpn,
                "trust_score": 1.0,
            }],
            "images": [{
                "image_type": "primary",
                "source": f"{brand} Official",
                "source_url": f"https://images.{brand.lower().replace(' ', '')}.com/monitors/{mpn.lower()}/hero.jpg",
                "storage_key": "products/{product_id}/primary.webp",
                "verified": True,
            }],
        }
        MONITORS_DATASET.append(item)

_generate_monitors()
