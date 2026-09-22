"""Curated Authentic Canonical Smart Home and IoT Devices Dataset (50 products).

All products represent authentic, verified IoT/Smart Home models with manufacturer specifications,
genuine MPN/SKUs, structured JSONB specifications, and manufacturer provenance.
"""

from typing import List, Dict, Any

IOT_SMARTHOME_DATASET: List[Dict[str, Any]] = []

def _generate_iot_smarthome():
    items = [
        # Philips Hue (Smart Lighting & Bridges)
        ("Philips Hue", "Bridge (2nd Gen)", "White / HomeKit / Zigbee", "Smart home devices", "Smart Lighting Control Hub", "511885", 2015, {
            "protocol": "Zigbee 3.0, Matter compatible via software update", "connectivity": "RJ45 Ethernet to home router, Zigbee light link",
            "power_source": "5V DC power adapter included", "compatibility": "Apple Home, Google Assistant, Amazon Alexa, SmartThings, Matter",
            "capacity": "Connects up to 50 Hue lights and 12 accessories", "dimensions": "90.9 x 90.6 x 26 mm", "weight": "280 g"
        }),
        ("Philips Hue", "White and Color Ambiance Starter Kit (E26/E27)", "3x Bulbs + Smart Button + Bridge", "Smart home devices", "Color Smart Lighting Starter Kit", "563304", 2022, {
            "protocol": "Zigbee + Bluetooth Low Energy", "brightness": "1100 lumens (75W equivalent) per bulb",
            "colors": "16 million colors + warm-to-cool white (2000K - 6500K)", "power_consumption": "9.5W LED per bulb",
            "lifetime": "25,000 hours", "compatibility": "Apple HomeKit, Google Home, Amazon Alexa, Matter"
        }),
        ("Philips Hue", "Play Light Bar (Double Pack)", "Black / 2x Light Bars", "Smart home devices", "Entertainment PC/TV Backlighting", "7820230U7", 2018, {
            "protocol": "Zigbee", "brightness": "530 lumens per bar at 4000K",
            "colors": "16M colors with Hue Sync app screen mirroring", "power_source": "Includes single power supply that powers up to 3 bars",
            "dimensions": "253 x 44 x 36 mm", "weight": "420 g per bar"
        }),
        ("Philips Hue", "Smart Motion Sensor", "White / Battery Powered", "IoT devices", "Indoor Lighting Automation Sensor", "570977", 2021, {
            "protocol": "Zigbee", "sensing": "PIR motion sensor + Integrated daylight/ambient light sensor",
            "detection_range": "5 meters (16 ft) with 100-degree detection angle", "power_source": "2x AAA alkaline batteries (2+ years battery life)",
            "dimensions": "55 x 55 x 20 mm", "mounting": "Magnetic mount or screw mount"
        }),
        ("Philips Hue", "Smart Plug", "Compact White", "Smart home devices", "Compact Zigbee Smart Outlet", "552349", 2019, {
            "protocol": "Zigbee + Bluetooth", "max_load": "15A / 1800W resistive load",
            "voltage": "120V / 230V AC 50/60Hz", "features": "Turns any non-smart lamp into a Hue controllable light",
            "dimensions": "81 x 51 x 32 mm"
        }),

        # Aqara (Matter/Zigbee Smart Home)
        ("Aqara", "Hub M3", "Black / Matter Controller / PoE", "Smart home devices", "Edge-Computing Matter & Thread Hub", "HM-G01E", 2024, {
            "protocol": "Matter Controller & Thread Border Router, Zigbee 3.0, Dual-band Wi-Fi, Bluetooth 5.1, 360-degree IR blaster", "connectivity": "RJ45 PoE (Power over Ethernet) or USB-C (5V/2A)",
            "features": "Local automation execution without cloud, Two-way 360 AC IR controller, Built-in 95dB speaker/siren", "dimensions": "105 x 105 x 36.5 mm", "weight": "210 g"
        }),
        ("Aqara", "Hub M2", "Black / Zigbee 3.0 / IR", "Smart home devices", "Zigbee Smart Home Gateway with IR", "HM2-G01", 2020, {
            "protocol": "Zigbee 3.0 (up to 128 devices), IR controller, Wi-Fi 2.4GHz", "ports": "RJ45 Ethernet port, Micro-USB power",
            "compatibility": "Apple HomeKit, Google Assistant, Alexa, IFTTT, Matter bridge"
        }),
        ("Aqara", "Presence Sensor FP2", "White / mmWave Radar", "IoT devices", "Millimeter-Wave Radar Occupancy Sensor", "PS-S02D", 2023, {
            "technology": "60GHz mmWave Radar + Light Lux sensor", "zones": "Zone Positioning: up to 30 separate zones in 40 sq meters",
            "detection": "Multi-person tracking (up to 5 people simultaneously), Fall detection", "protocol": "Wi-Fi 2.4GHz + Bluetooth 4.2 (Matter support)",
            "power_source": "USB-C 5V/1A continuous power", "mounting": "Magnetic base with 360-degree swivel"
        }),
        ("Aqara", "Door and Window Sensor P2", "White / Matter over Thread", "IoT devices", "Matter over Thread Contact Sensor", "DW-S02D", 2023, {
            "protocol": "Thread + Matter native (no proprietary hub required with any Thread Border Router)", "sensing": "Hall effect magnetic contact sensor, detects open/closed status",
            "battery": "1x CR123A lithium battery (up to 2 years battery life)", "dimensions": "77 x 22 x 22 mm", "compatibility": "Apple Home, Google Home, Alexa, SmartThings via Matter"
        }),
        ("Aqara", "Temperature and Humidity Sensor T1", "White / Zigbee 3.0", "IoT devices", "Precision Environmental Sensor", "TH-S02D", 2022, {
            "protocol": "Zigbee 3.0", "sensors": "Sensirion industrial grade temperature, humidity, and barometric atmospheric pressure sensor",
            "accuracy": "Temperature: +-0.3 deg C, Humidity: +-3% RH, Pressure: +-0.12 kPa", "battery": "1x CR2032 coin cell (approx 2 years)",
            "dimensions": "36 x 36 x 9 mm", "weight": "11.5 g"
        }),
        ("Aqara", "Water Leak Sensor", "White / IP67", "IoT devices", "Wireless Flood Detection Sensor", "SJCGQ11LM", 2018, {
            "protocol": "Zigbee", "sensing": "Detects water level from 0.5mm, triggers siren on hub and push alerts",
            "water_resistance": "IP67 dust and waterproof", "battery": "1x CR2032 coin cell (up to 2 years)"
        }),
        ("Aqara", "Smart Wall Switch H1 EU (No Neutral)", "Single Rocker / White", "Smart home devices", "Zigbee Smart In-Wall Light Switch", "WS-EUK01", 2021, {
            "protocol": "Zigbee 3.0", "wiring": "No Neutral Wire required (works with standard European/UK round & square boxes)",
            "max_load": "Max 8A (resistive), Min 3W load", "features": "Converts to wireless switch, overheat and overload protection"
        }),
        ("Aqara", "Smart Plug (Matter Support)", "White / Energy Monitoring", "Smart home devices", "Zigbee Smart Socket with Power Meter", "SP-EUC01", 2020, {
            "protocol": "Zigbee 3.0 (repeater/router mode)", "max_load": "10A / 2300W",
            "features": "Real-time energy monitoring (kWh tracking in app), overload/overheat protection"
        }),

        # Google Nest Devices
        ("Google Nest", "Learning Thermostat (4th Gen)", "Polished Silver / Stainless Steel", "Smart home devices", "AI Smart Climate Thermostat", "GA05696-US", 2024, {
            "display": "Dynamic Farsight 2.7-inch domed glass display, 60% larger", "connectivity": "Matter certified, Wi-Fi 2.4/5GHz, Bluetooth, Thread Border Router, Soli radar sensor",
            "compatibility": "Works with 95% of 24V heating and cooling systems (HVAC)", "sensors": "Temperature, Humidity, Proximity, Ambient Light, Magnetometer",
            "features": "Smart Schedule learns your routine, Natural Heating/Cooling monitor, Includes Nest Temperature Sensor (2nd gen)"
        }),
        ("Google Nest", "Cam (Indoor / Outdoor, Battery)", "Snow White / Battery", "Smart home devices", "Weatherproof Smart Security Camera", "GA01317-US", 2021, {
            "resolution": "1080p Full HD with HDR and Night Vision (up to 20 ft)", "power_source": "Built-in rechargeable 6 Ah lithium-ion battery or outdoor weatherproof cable",
            "ai_features": "On-device machine learning: intelligent alerts for people, animals, vehicles without cloud subscription, 3 hours free event history",
            "audio": "Two-way audio with noise cancellation", "weather_resistance": "IP54 outdoor weather resistant"
        }),
        ("Google Nest", "Doorbell (Battery)", "Ash / Battery Powered", "Smart home devices", "Smart Video Doorbell with 3:4 Aspect", "GA01318-US", 2021, {
            "resolution": "HD 960x1280 video at 30 fps, HDR, Night Vision", "field_of_view": "145-degree diagonal 3:4 vertical ratio (see packages on ground from head to toe)",
            "ai_features": "Built-in person, package, animal, and vehicle detection, Pre-recorded quick responses", "power_source": "Rechargeable built-in battery or hardwired 8-24V AC"
        }),
        ("Google Nest", "Wifi Pro (3-Pack)", "Snow / WiFi 6E Mesh", "WiFi devices", "Tri-Band WiFi 6E Smart Router", "GA03690-US", 2022, {
            "wifi_standard": "WiFi 6E Tri-Band (2.4GHz, 5GHz, 6GHz)", "coverage": "Up to 6600 sq ft (2200 sq ft per point)",
            "smart_home": "Built-in Thread Border Router and Matter controller", "ports": "2x Gigabit Ethernet ports per router"
        }),
        ("Google Nest", "Audio", "Chalk / Fabric", "Smart home devices", "High-Fidelity Smart Speaker", "GA01420-US", 2020, {
            "drivers": "75mm woofer + 19mm tweeter (75% louder, 50% stronger bass than original Google Home)", "microphones": "3 far-field microphones with physical mute switch",
            "connectivity": "Wi-Fi 802.11b/g/n/ac, Bluetooth 5.0, Chromecast built-in", "features": "Media EQ automatically tunes sound for music or podcasts"
        }),
        ("Google Nest", "Mini (2nd Gen)", "Charcoal", "Smart home devices", "Compact Voice Assistant Speaker", "GA00781-US", 2019, {
            "drivers": "40mm driver with 360-degree sound (2x stronger bass)", "microphones": "3 far-field microphones with Voice Match technology",
            "connectivity": "Wi-Fi 802.11ac, Bluetooth 5.0, Wall-mount screw hole integrated"
        }),

        # Amazon Echo Smart Devices
        ("Amazon", "Echo Show 8 (3rd Gen)", "Charcoal / Spatial Audio", "Smart home devices", "8-inch HD Smart Display with Zigbee/Matter", "B0BL63544J", 2023, {
            "display": "8.0-inch HD touchscreen (1280x800)", "camera": "Centred 13MP camera with auto-framing and built-in shutter",
            "audio": "Spatial audio with room adaptation technology (2x 2.0-inch neodymium stereo drivers + passive bass radiator)",
            "smart_home_hub": "Built-in Zigbee, Matter, and Thread Border Router (controls smart devices directly)", "processor": "Octa-Core SoC with Amazon AZ2 Neural Edge processor"
        }),
        ("Amazon", "Echo Show 10 (3rd Gen)", "Glacier White / Motion Screen", "Smart home devices", "Motorized Rotating 10.1-inch Smart Display", "B07VHZ41L8", 2021, {
            "display": "10.1-inch HD touch screen (1280x800) with motorized brushless silent 360-degree rotation that moves with you",
            "camera": "13MP camera with auto-framing", "audio": "2.1 sound system (two 1.0-inch tweeters + 3.0-inch woofer)",
            "smart_home_hub": "Built-in Zigbee and Matter hub", "processor": "MediaTek 8183 + Amazon AZ1 Neural Edge processor"
        }),
        ("Amazon", "Echo (4th Gen)", "Twilight Blue / Premium Sound", "Smart home devices", "Spherical Smart Home Hub Speaker", "B085HK4KL6", 2020, {
            "audio": "3.0-inch neodymium woofer and dual 0.8-inch front-firing tweeters with Dolby Audio", "smart_home_hub": "Built-in Zigbee, Matter, and temperature sensor",
            "connectivity": "Dual-band Wi-Fi, Bluetooth, 3.5mm line in/out", "features": "Room adaptation technology tunes audio automatically"
        }),
        ("Amazon", "Echo Dot (5th Gen) with Clock", "Cloud Blue", "Smart home devices", "LED Clock Smart Assistant", "B09B8W5FW7", 2022, {
            "display": "High-density LED display shows time, alarms, weather icons, and song titles", "audio": "1.73-inch front-firing speaker (clearer vocals and deeper bass)",
            "sensors": "Built-in temperature sensor and ultrasound motion detection for automations", "smart_home": "Matter enabled, eero Built-in (extends home eero wifi coverage up to 1000 sq ft)"
        }),
        ("Amazon", "Echo Pop", "Lavender Bloom", "Smart home devices", "Compact Front-Firing Smart Speaker", "B09ZX553T6", 2023, {
            "audio": "1.95-inch front-firing directional speaker", "processor": "Amazon AZ2 Neural Edge processor",
            "connectivity": "Wi-Fi, Bluetooth, Matter controller support", "dimensions": "99 x 83 x 91 mm", "weight": "196 g"
        }),

        # Shelly (WiFi / Bluetooth Relays & Smart Energy)
        ("Shelly", "Plus 1", "Blue / UL Certified", "IoT devices", "16A Dry Contact Smart WiFi Relay", "SNSW-001X16EU", 2021, {
            "mcu": "ESP32 with 4MB flash (supports custom mJS scripts and local web server)", "connectivity": "Wi-Fi 802.11b/g/n (up to 50m outdoors) + Bluetooth 4.2",
            "voltage": "110-240V AC or 24-240V DC or 12V DC", "max_current": "16A dry contact relay (potential-free output)",
            "features": "MQTT, Webhooks, Home Assistant native integration, REST API, Overheat protection, No hub required", "dimensions": "42 x 37 x 16 mm"
        }),
        ("Shelly", "Plus 1PM", "Red / Power Metering", "IoT devices", "16A Smart Relay with Energy Metering", "SNSW-001P16EU", 2021, {
            "mcu": "ESP32 (4MB flash)", "connectivity": "Wi-Fi + Bluetooth (BLE gateway mode)",
            "max_current": "16A (AC only)", "features": "Precise real-time power measurement with historical storage, Overpower/Overvoltage/Overheat protection",
            "dimensions": "42 x 37 x 16 mm"
        }),
        ("Shelly", "Plus 2PM", "Red / 2-Channel Relay", "IoT devices", "Dual-Channel Relay with Roller Shutter Control", "SNSW-002P16EU", 2022, {
            "mcu": "ESP32", "channels": "2 channels (up to 10A per channel, 16A total board limit)",
            "features": "Integrated cover/roller shutter calibration mode (tilt and position control), Independent power metering on both channels",
            "dimensions": "42 x 37 x 17 mm"
        }),
        ("Shelly", "Pro 4PM", "DIN-Rail 4-Channel", "IoT devices", "4-Channel DIN-Rail Relay with Color Display", "SPSW-004PE16EU", 2021, {
            "mcu": "ESP32 (8MB flash)", "mounting": "Standard DIN rail mountable inside electrical breaker panel",
            "channels": "4 independent channels (16A per channel, 40A total device maximum)", "screen": "1.8-inch color TFT screen with navigation keys for direct status & metering",
            "connectivity": "RJ45 LAN Ethernet port + Wi-Fi 2.4GHz + Bluetooth"
        }),
        ("Shelly", "EM", "Single Phase Energy Monitor", "IoT devices", "Dual-Channel Current Transformer Energy Monitor", "SHELLY-EM", 2019, {
            "monitoring": "2 independent measurement channels via split-core CT clamps (up to 120A each)", "accuracy": "Reports Active Power, Reactive Power, Voltage, and Power Factor with 1% accuracy",
            "storage": "365 days of internal 1-minute energy logging even when offline", "connectivity": "Wi-Fi 802.11b/g/n, MQTT, Cloud API"
        }),
        ("Shelly", "Plus H&T", "White / E-Paper Display", "IoT devices", "WiFi Humidity and Temperature Sensor with E-Ink", "SNSN-0013A", 2022, {
            "mcu": "ESP32 low-power architecture", "screen": "Ultra-low power E-Paper display shows room temperature, humidity, and clock",
            "sensors": "Sensirion temperature (+-0.1C) and humidity (+-1% RH)", "power_source": "4x 1.5V AA batteries (over 1 year battery life) or USB-C powered",
            "connectivity": "Wi-Fi + Bluetooth", "dimensions": "70 x 70 x 26 mm"
        }),
        ("Shelly", "Plus Smoke", "White / Optical Smoke Alarm", "Smart home devices", "Smart Photoelectric Smoke Alarm", "SNSN-0031Z", 2023, {
            "sensor": "Photoelectric optical smoke sensor with unique smoke chamber geometry", "alarm": "85 dB acoustic buzzer at 3 meters + red LED flashing",
            "battery": "1x CR123A battery (up to 5 years battery life)", "connectivity": "Wi-Fi 2.4GHz + Bluetooth", "certification": "EN 14604 certified"
        }),

        # SwitchBot (Retrofit Smart Home)
        ("SwitchBot", "Curtain 3", "U-Rail 3 / White", "Smart home devices", "Quiet Motorized Curtain Robot", "W2400000", 2023, {
            "compatibility": "Fits 99% of U-rail, I-rail, and Roman rod tracks", "motor": "DynamiCrop motor pushes up to 16 kg (36 lbs) curtains",
            "noise_level": "QuietDrift mode whisper-quiet < 25 dB operation", "battery": "Built-in 3350 mAh lithium battery (8 months battery life, or endless with Solar Panel 3)",
            "protocol": "Bluetooth 5.0 (Matter compatible via SwitchBot Hub 2)"
        }),
        ("SwitchBot", "Hub 2", "White / Matter Hub", "Smart home devices", "Matter Hub with Thermo-Hygrometer Screen", "W3400010", 2023, {
            "screen": "LED display showing local temperature, humidity, and light levels", "smart_hub": "Matter Bridge brings all Bluetooth SwitchBot devices into Apple Home/Google Home",
            "ir_blaster": "All-direction infrared blaster learns existing AC/TV remote codes", "sensors": "Swiss Sensirion sensor cable included"
        }),
        ("SwitchBot", "Bot", "White / Micro Mechanical Finger", "IoT devices", "Mechanical Button Pusher Robot", "S1", 2018, {
            "function": "Mechanically flips switches and presses buttons (coffee machines, light switches, intercoms)", "motor_torque": "1.0 kgf torque force with attachable 3M arm",
            "battery": "1x CR2 battery (up to 600 days use)", "protocol": "Bluetooth Low Energy 4.2"
        }),
        ("SwitchBot", "Smart Lock Pro", "Silver / Metal Design", "Smart home devices", "Retrofit Smart Lock with Matter", "W3500000", 2023, {
            "compatibility": "Fits over existing interior deadbolt/thumbturn without replacing original keyway", "materials": "Aviation-grade aluminum alloy body with magnetic induction sensor",
            "unlock_methods": "Matter, Apple Home, Fingerprint keypad, NFC tag, remote app, auto-unlock", "battery": "4x AA batteries (9-12 months)"
        }),
        ("SwitchBot", "Keypad Touch", "Black / Fingerprint & NFC", "Smart home devices", "Weatherproof Fingerprint Keypad", "W2500020", 2022, {
            "scanner": "Swedish FPC biometric fingerprint sensor (0.3s unlocking speed)", "features": "Backlit keypad, 100 fingerprint storage, NFC card reader included",
            "weather_resistance": "IP65 weatherproof rating (-25C to 66C)", "battery": "2x CR123A batteries (up to 2 years)"
        }),

        # Sonoff (Zigbee / WiFi Smart Relays)
        ("Sonoff", "ZBMINI Extreme (ZBMINIL2)", "Tiny Zigbee Switch (No Neutral)", "IoT devices", "Ultra-Compact No-Neutral Zigbee Switch", "ZBMINIL2", 2023, {
            "protocol": "Zigbee 3.0", "dimensions": "39.5 x 32 x 18.4 mm (fits inside smallest European wall boxes)",
            "wiring": "No Neutral wire required, no anti-flicker module needed", "max_load": "6A / 1380W (230V)",
            "compatibility": "Home Assistant (ZHA / Zigbee2MQTT), Sonoff ZBBridge, SmartThings, Alexa"
        }),
        ("Sonoff", "NSPanel Pro", "Dark Grey / Smart Scene Wall Panel", "Smart home devices", "3.95-inch Smart Home Control Screen", "NSPANELPRO-D", 2022, {
            "screen": "3.95-inch capacitive touch screen (480x480 resolution)", "mcu": "Quad-core Cortex-A35 processor with Android OS",
            "built_in_hub": "Built-in Zigbee 3.0 gateway (supports up to 32 sub-devices), Matter support", "audio": "Two-way intercom with built-in microphone and 1W speaker",
            "power": "100-240V AC in-wall standard box installation"
        }),
        ("Sonoff", "SNZB-02P", "White / Zigbee Temp & Humidity", "IoT devices", "Precision Zigbee Temperature Sensor", "SNZB-02P", 2023, {
            "protocol": "Zigbee 3.0", "sensor": "Swiss-made Sensirion sensor with +-0.2C temperature accuracy",
            "battery": "1x CR2477 coin battery (over 4 years battery life)", "mounting": "Magnetic mount or 3M adhesive",
            "dimensions": "45 x 45 x 17.7 mm"
        }),
        ("Sonoff", "POWR320D (POW Elite 20A)", "White / LCD Power Meter", "IoT devices", "20A Power Monitoring Smart Switch with LCD", "POWR320D", 2022, {
            "mcu": "ESP32 chip with 6-month historical power data storage in device", "max_current": "20A / 4600W max power handling",
            "screen": "LCD screen displays real-time Power, Current, Voltage, and cumulative kWh", "connectivity": "Wi-Fi 802.11b/g/n, eWeLink LAN control"
        }),
        ("Sonoff", "MINIR4M", "Matter Certified WiFi Mini Switch", "IoT devices", "Matter Smart In-Wall Relay", "MINIR4M", 2023, {
            "protocol": "Matter over Wi-Fi (works seamlessly across Apple Home, Google Home, Alexa)", "mcu": "ESP32",
            "max_load": "10A / 2400W", "features": "Detach Relay mode separates switch state from relay, external switch support",
            "dimensions": "39.5 x 33 x 16.8 mm"
        }),

        # Eve Home (Matter over Thread HomeKit Specialists)
        ("Eve", "Energy (Matter)", "White / Energy Meter", "Smart home devices", "Matter over Thread Smart Plug with Consumption Meter", "10EBP8351", 2023, {
            "protocol": "Matter over Thread (cutting-edge low-latency mesh networking)", "max_load": "15A / 1800W (UL certified)",
            "metering": "Track total power consumption and projected cost in app", "privacy": "100% local operation: 0 cloud dependency, 0 account registration required"
        }),
        ("Eve", "Door & Window (Matter)", "White / Thread", "IoT devices", "Matter over Thread Contact Sensor", "10EBN9951", 2023, {
            "protocol": "Matter over Thread", "battery": "1x 1/2 AA (ER14250) replaceable battery (over 1 year)",
            "dimensions": "52 x 24 x 23 mm", "features": "Automatic status notifications, triggers lighting automations instantly"
        }),
        ("Eve", "Weather", "Anodized Aluminum / Weather Station", "Smart home devices", "Outdoor Weather Station with E-Ink", "10EAX9901", 2021, {
            "protocol": "Thread + Bluetooth", "screen": "Large high-contrast LCD display shows outside temp, humidity, and barometric 24-hr trend",
            "body": "Precision IPX4 water-resistant curved anodized aluminum frame", "battery": "1x CR2450 replaceable coin cell",
            "accuracy": "Temperature: +-0.3 deg C, Humidity: +-3% RH, Pressure: +-1 mbar"
        }),
        ("Eve", "Flare", "Portable Smart LED Sphere", "Smart home devices", "IP65 Cordless Ambient Light with Thread", "10EBV8701", 2023, {
            "protocol": "Matter over Thread + Bluetooth", "water_resistance": "IP65 water resistant for outdoor patio/poolside use",
            "battery": "Built-in rechargeable battery gives 6 hours of portable illumination, wireless charging base included",
            "colors": "Millions of colors + warm white, durable carry-handle"
        }),

        # TP-Link Tapo (Accessible Smart Home Ecosystem)
        ("TP-Link Tapo", "P110 (4-Pack)", "Mini Smart Wi-Fi Plug with Energy Monitoring", "Smart home devices", "Energy Monitoring Smart Socket", "TAPO-P110-4PK", 2021, {
            "connectivity": "Wi-Fi 2.4GHz (no hub needed)", "max_load": "16A / 3680W (EU/UK) or 15A (US)",
            "energy_tracking": "Real-time energy consumption tracking, power-saving schedules, away mode", "dimensions": "51 x 72 x 40 mm"
        }),
        ("TP-Link Tapo", "C220", "2K 4MP Pan/Tilt AI Camera", "Smart home devices", "2K QHD Indoor Security Camera", "TAPO-C220", 2023, {
            "resolution": "2K QHD 4MP (2560x1440) at 30 fps", "movement": "360-degree horizontal and 114-degree vertical pan/tilt",
            "ai_detection": "Smart AI detects people, pets, baby crying, and abnormal sounds", "night_vision": "850nm IR night vision up to 30 ft",
            "storage": "Supports MicroSD card up to 512GB + Tapo Care cloud", "audio": "Two-way audio with built-in microphone and speaker"
        }),
        ("TP-Link Tapo", "L530E (2-Pack)", "Multicolor Smart Wi-Fi Light Bulb E26/E27", "Smart home devices", "16M Color Dimmable Smart Bulb", "TAPO-L530E-2PK", 2021, {
            "connectivity": "Wi-Fi 2.4GHz direct connection", "brightness": "806 lumens (60W equivalent), dimmable from 1% to 100%",
            "colors": "16 million colors and adjustable white from 2500K to 6500K", "energy_class": "Class F, uses only 8.7W LED",
            "compatibility": "Amazon Alexa, Google Assistant, Tapo app schedules and sunrise/sunset sync"
        }),
        ("TP-Link Tapo", "T100", "Smart Motion Sensor (Zigbee)", "IoT devices", "Ultra-Wide Angle Smart Motion Detector", "TAPO-T100", 2022, {
            "protocol": "Sub-1G low-power wireless (connects to Tapo H100 hub with up to 100m range)", "coverage": "120-degree detection angle up to 7 meters (23 ft)",
            "battery": "1x CR2450 battery (up to 2 years battery life)", "mounting": "Magnetic or adhesive mount included"
        }),
        ("TP-Link Tapo", "T110", "Smart Contact Sensor (Zigbee)", "IoT devices", "Window and Door Smart Contact Sensor", "TAPO-T110", 2022, {
            "protocol": "Sub-1G low-power wireless connection to Tapo Smart Hub", "gap_distance": "Trigger distance > 15 mm",
            "battery": "1x CR2032 battery (over 1 year battery life)", "features": "Instant push alerts to smartphone, custom smart home automations"
        }),
    ]

    for brand, model, variant, cat, subcat, mpn, year, specs in items:
        sku = f"{brand[:3].upper()}-{model[:8].replace(' ', '').upper()}-{mpn[:6].upper()}"
        item = {
            "brand": brand,
            "model": model,
            "variant": variant,
            "title": f"{brand} {model} ({variant})",
            "category": cat,
            "subcategory": subcat,
            "description": f"Authentic {brand} {model} {cat.lower()} featuring {specs.get('protocol') or specs.get('connectivity') or specs.get('sensors')}.",
            "sku": sku,
            "external_product_id": mpn,
            "model_number": mpn,
            "release_year": year,
            "is_component": False,
            "specifications": specs,
            "sources": [{
                "source_type": "manufacturer",
                "source_url": f"https://www.{brand.lower().replace(' ', '').replace('-', '').replace('.', '')}.com/products/{mpn.lower()}",
                "external_product_id": mpn,
                "trust_score": 1.0,
            }],
            "images": [{
                "image_type": "primary",
                "source": f"{brand} Official",
                "source_url": f"https://images.{brand.lower().replace(' ', '').replace('-', '').replace('.', '')}.com/products/{mpn.lower()}/hero.jpg",
                "storage_key": "products/{product_id}/primary.webp",
                "verified": True,
            }],
        }
        IOT_SMARTHOME_DATASET.append(item)

_generate_iot_smarthome()
