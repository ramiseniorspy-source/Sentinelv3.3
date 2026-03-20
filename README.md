# 🛠️ Setup & Prerequisites

To run **AF Project Sentinel**, ensure your environment meets these requirements:

## 1. Local AI Engine (Ollama)
Sentinel relies on a local Ollama instance for secure, offline analysis.
- **Install Ollama:** [https://ollama.com/](https://ollama.com/)
- **Pull the Model:** Open your terminal and run:
  ```bash
  ollama pull llama3
  ```
- **Ensure Service is Running:** Ollama must be active (`ollama serve`) before running the script.

## 2. Python Environment
- **Python Version:** 3.10 or higher recommended.
- **Required Libraries:**
  ```bash
  pip install requests
  ```
  *(Note: `os`, `sys`, `pathlib`, and `concurrent.futures` are part of the Python Standard Library.)*

## 3. Hardware Requirements
- **Storage:** Designed for high-speed scanning of large volumes (HDD/SSD up to 2TB+).
- **GPU (Optional but Recommended):** The script automatically detects AMD/NVIDIA VRAM to scale processing. If no GPU is found, it will default to 2 CPU threads.

## 4. Usage
Place `AF_Project_Sentinel_v3_3.py` in the directory you wish to audit and run:
```bash
python AF_Project_Sentinel_v3_3.py
```
Outputs will be generated in the `AF_System_Manifests` folder and a master `AF_MASTER_AUDIT.md` file.
