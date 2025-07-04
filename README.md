# MCU Code Analyzer

A professional MCU project code analysis tool with intelligent chip recognition, code structure analysis, and LLM-powered smart analysis capabilities.

## 🚀 Features

### Core Analysis Capabilities
- **Multi-platform Project Support**: Keil (.uvprojx), CMake, Makefile, Visual Studio projects
- **Intelligent Chip Recognition**: STM32, NXP, Microchip, TI and other mainstream MCU vendors
- **Code Structure Analysis**: Function definitions, call relationships, main function reachability analysis
- **Interface Usage Analysis**: GPIO, UART, I2C, SPI, ADC, TIMER, DMA interface statistics
- **Call Flow Visualization**: Generate function call flowcharts and relationship diagrams

### LLM Intelligence Integration
- **Multi-LLM Support**: Ollama (local), OpenAI, Tencent Cloud APIs
- **Smart Code Summarization**: Automatic project functionality analysis
- **Semantic Analysis**: Code quality assessment and optimization suggestions
- **Intelligent Documentation**: Auto-generate technical documentation

### Modern User Interface
- **Professional GUI**: Modern interface design with CustomTkinter
- **Multi-language Support**: English/Chinese internationalization
- **Real-time Progress**: Live analysis progress feedback
- **Multi-tab Results**: Organized result presentation

## 📋 System Requirements

- Python 3.8+
- Windows 10/11 (primary support)
- 4GB+ RAM recommended
- Internet connection (for LLM services)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/MCU_Code_Analyzer.git
cd MCU_Code_Analyzer
```

2. Install dependencies:
```bash
pip install -r mcu_code_analyzer/requirements.txt
```

3. Run the application:
```bash
python mcu_code_analyzer/main_gui.py
```

## 📖 Usage

1. **Select MCU Project**: Browse and select your MCU project directory
2. **Configure Analysis**: Set analysis depth and options
3. **Start Analysis**: Click "Start Analysis" to begin code analysis
4. **View Results**: Browse analysis results in multiple tabs
5. **LLM Analysis**: Use AI-powered analysis for deeper insights

## 🏗️ Architecture

The project follows a three-layer architecture:

- **UI Layer**: User interface components (main_window, config_dialog, result_viewer)
- **Intelligence Layer**: LLM integration (llm_manager, code_summarizer, semantic_analyzer)
- **Core Layer**: Analysis engines (chip_detector, code_analyzer, interface_analyzer)
- **Utils Layer**: Supporting utilities (config, logger, file_utils)

## 🔧 Configuration

Edit `mcu_code_analyzer/config.yaml` to configure:
- LLM service settings (Ollama, OpenAI, Tencent Cloud)
- Analysis parameters
- UI preferences
- Output formats

## 📊 Supported MCU Platforms

### STM32 Series
- STM32F0/F1/F2/F3/F4/F7 series
- STM32G0/G4 series  
- STM32H7 series
- STM32L0/L1/L4 series

### NXP Platforms
- LPC series
- Kinetis series
- i.MX RT series

### Other Vendors
- Microchip PIC/SAM series
- Texas Instruments MSP430/TM4C/CC series

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For questions and support, please open an issue on GitHub.
