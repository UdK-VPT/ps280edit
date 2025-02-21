# PS-280 Climate Sensor Editor

**Author:** Werner Kaul-Gothe  
**Department:** VPT  
**Organisation:** Universität der Künste Berlin IAS  
**Date:** 2025-02-20  

---

## 📋 Overview

The **PS-280 Climate Sensor Editor** is a specialized configuration and management tool designed for the **PS-280 Climate Sensor** developed by **PIKK-Systems**, Berlin, Germany. This editor allows users to interact with, configure, and manage climate sensors through a user-friendly interface. It supports firmware updates, MQTT topic management, and sensor configuration directly from YAML/TOML configuration files.

---

## 🚀 Features

- ✅ **Configuration Management**: Edit and manage sensor settings through intuitive forms.
- 🔗 **MQTT Integration**: Set and manage MQTT topics for seamless communication.
- 💾 **Firmware Management**: Upload, update, and erase firmware directly from the editor.
- 🖼️ **Sticker Generation**: Automatically generate stickers and QR codes for device identification.
- 🛠️ **Cross-Platform Compatibility**: Compatible with Windows, macOS, and Linux.

---

## 🛠️ Requirements

Make sure you have Python 3.8+ installed. Install all dependencies using:

```bash
pip install -r requirements.txt
```

### 📦 Required Python Packages

- [**esptool**](https://pypi.org/project/esptool/) (v4.8.1): For flashing firmware on ESP-based microcontrollers.
- [**flet**](https://pypi.org/project/flet/) (v0.26.0): To build cross-platform user interfaces.
- [**IPython**](https://pypi.org/project/ipython/) (v8.27.0 / v8.12.3): Enhanced interactive Python shell for testing and development.
- [**Pillow**](https://pypi.org/project/Pillow/) (v11.1.0): Image processing library used for QR code and sticker generation.
- [**platformdirs**](https://pypi.org/project/platformdirs/) (v4.3.6): Manage platform-specific directories easily.
- [**pyserial**](https://pypi.org/project/pyserial/) (v3.5): Provides serial communication capabilities.
- [**PyYAML**](https://pypi.org/project/PyYAML/) (v6.0.2): YAML parsing and serialization library.
- [**segno**](https://pypi.org/project/segno/) (v1.6.1): Generate QR codes.
- [**toml**](https://pypi.org/project/toml/) (v0.10.2): Parse and write TOML configuration files.

---

## 🔧 Installation

1. **Clone the Repository**

```bash
git clone https://github.com/UdK-VPT/ps280edit.git
cd ps280-climate-editor
```

2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

3. **Build the Application (Optional)**

Use PyInstaller to create a standalone executable. You may have to install it.

- [**PyInstaller**](https://pypi.org/project/pyinstaller/) (v5.13.2): Converts Python applications into standalone executables.

A standalone executable is created by:

```bash
python build.py
```

---

## ⚙️ Configuration

It is not very likely that the ininitial configuration has to be changed. Everything should work right out of the box. The editor uses a YAML configuration file named `ps280edit.yaml`. 

---

## 🎮 Usage

Run the PS-280 editor as python script with:

```bash
python src/ps280edit.py
```

Or run the built executable from the `app` folder:

```bash
./app/PS280Edit.exe  # On Windows
```

---

## 🖥️ Features Breakdown

### 📂 **Configuration Editor**
- Load and modify TOML configuration files.
- Automatically validate settings before saving.

### 🔗 **MQTT Topic Management**
- Set topics for sensor communication.
- Automatically configure download/upload topics.

### 🔥 **Firmware Management**
- Upload and flash firmware directly to the device.
- Erase existing firmware before flashing new versions.

### 🏷️ **Sticker & QR Code Generation**
- Generate QR codes with sensor information.
- Export stickers as high-resolution images.

---

## 🐛 Troubleshooting

| Issue                        | Solution                                                      |
|------------------------------|---------------------------------------------------------------|


---

## 🙌 Contribution Guidelines

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to your branch (`git push origin feature-branch`).
5. Open a **Pull Request**.

---

## 📜 License

This project is licensed under the [GNU Affero General Public License v3.0 (AGPL-3.0)](https://www.gnu.org/licenses/agpl-3.0.en.html).

### 🔔 Requirements

- You **may use** this software commercially.
- You **must disclose** your source code if you distribute modified versions.
- You **must provide attribution** to the original author:
  - Include the following in any distribution or modification:
    ```
    Original Author: Werner Kaul-Gothe
    Department: VPT
    Organisation: Universität der Künste Berlin IAS
    ```
- Please inform the author of any commercial use or deployment as a courtesy.

---

## 📞 Contact

For support or inquiries, please contact:

- **Werner Kaul-Gothe**  
  Department VPT  
  Universität der Künste Berlin IAS  
  📧 [we.kaul@udk-berlin.de](mailto:we.kaul@udk-berlin.de)

---

## 🎉 Acknowledgments

Special thanks to **PIKK-Systems**, Berlin, Germany, for supporting this development.
