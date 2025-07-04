"""
Language localization module for MCU Code Analyzer
Supports English and Chinese language switching
"""

import yaml
import os

def get_version():
    """Read version from config.yaml"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config.get('app', {}).get('version', '1.0.0')
    except:
        return '1.0.0'

def get_language_from_config():
    """Read language setting from config.yaml"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config.get('app', {}).get('language', 'en')
    except:
        return 'en'

def save_language_to_config(language):
    """Save language setting to config.yaml"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}

        if 'app' not in config:
            config['app'] = {}
        config['app']['language'] = language

        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        return True
    except:
        return False

class Localization:
    """Language localization class"""

    def __init__(self, language=None):
        # Load language from config file if not specified
        if language is None:
            language = get_language_from_config()
        self.language = language
        self.version = get_version()
        self.texts = {
            'en': {
                # Window titles
                'main_title': f'MCU Code Analyzer v{self.version}',
                'about_title': 'About',
                'config_title': 'Configuration',
                
                # Menu items
                'menu_config': 'Config',
                'menu_llm_config': 'LLM Config',
                'menu_analysis_settings': 'Analysis Settings',
                'menu_help': 'Help',
                'menu_usage': 'README',
                'menu_about': 'About',
                
                # Project settings
                'project_settings': 'Project Settings',
                'project_directory': 'MCU Project Directory:',
                'output_directory': 'Output Directory:',
                'browse': 'Browse',
                
                # Analysis options
                'analysis_options': 'Analysis Options',
                'deep_analysis': '✓ Deep Code Analysis',
                'call_analysis': 'Main Function Call Analysis',
                'generate_report': 'Generate Analysis Report',
                'call_depth': 'Call Depth:',
                'show_flowchart': 'Show Call Flowchart',
                
                # Control buttons
                'start_analysis': 'Start Analysis',
                'llm_analysis': 'LLM Analysis',
                'clear': 'Clear',
                'about': 'About',
                
                # Status and progress
                'ready': 'Ready',
                'analyzing': 'Analyzing...',
                'analysis_complete': 'Analysis Complete!',
                'analysis_failed': 'Analysis Failed',
                
                # Result tabs
                'project_overview': 'Project Overview',
                'detailed_analysis': 'Detailed Analysis',
                'call_flowchart': 'Call Flowchart',
                'execution_log': 'Execution Log',
                
                # Flowchart controls
                'refresh_flowchart': 'Refresh Flowchart',
                'render_graphics': 'Render Graphics',
                'export_code': 'Export Code',
                'mermaid_source': 'Mermaid Source',
                'graphics_preview': 'Graphics Preview',
                'render_graph': 'Render Graph',
                'clear_graph': 'Clear Graph',
                
                # Messages
                'select_project_dir': 'Please select MCU project directory',
                'select_output_dir': 'Please select output directory',
                'project_dir_not_exist': 'Project directory does not exist',
                'analysis_complete_msg': 'Analysis complete!\nResults saved to: {}',
                'no_flowchart': 'No flowchart to render, please run call analysis first',
                'no_mermaid_code': 'No Mermaid code to export',
                'save_mermaid_code': 'Save Mermaid Code',
                'mermaid_saved': 'Mermaid code saved to:\n{}',
                'save_failed': 'Save failed:\n{}',
                'render_failed': 'Render failed:\n{}',
                
                # File scanning
                'scanning_files': 'Scanning project files...',
                'detecting_chip': 'Detecting chip information...',
                'analyzing_code': 'Analyzing code structure...',
                'analyzing_calls': 'Analyzing call relationships...',
                'generating_flowchart': 'Generating call flowchart...',
                'generating_report': 'Generating analysis report...',
                
                # Statistics
                'found_source_files': 'Found source files: {} files',
                'found_header_files': 'Found header files: {} files',
                'found_project_files': 'Found project files: {} files',
                'found_functions': 'Found functions: {} functions',
                'main_function': 'main function',
                'detected_chip': 'Detected chip: {}',
                'detected_interfaces': 'Detected interfaces: {}',
                
                # Chip info
                'unknown': 'Unknown',
                'device': 'Device',
                'vendor': 'Vendor',
                'series': 'Series',
                'core': 'Core',
                
                # About dialog
                'about_text': f'''MCU Code Analyzer v{self.version}

Professional MCU project code analysis tool

Features:
• Intelligent chip detection
• Code flow diagram generation
• LLM intelligent analysis
• Multi-threaded processing
• Professional UI interface

Development Team: AI Assistant
Technical Support: Based on Claude AI''',
                
                # Error messages
                'error': 'Error',
                'warning': 'Warning',
                'info': 'Information',
                'success': 'Success',
                'failed': 'Failed',
                'cleanup_error': 'Error during cleanup: {}',
                'parse_error': 'Parse project file failed: {}',
                'analysis_error': 'Analysis failed: {}',
                'file_analysis_error': 'File analysis failed {}: {}',
                
                # Language settings
                'language': 'Language',
                'english': 'English',
                'chinese': 'Chinese',

                # LLM Configuration
                'llm_config': 'LLM Configuration',
                'select_llm_provider': 'Select LLM Provider',
                'config_params': 'Configuration Parameters',
                'save': 'Save',
                'cancel': 'Cancel',
                'config_saved': 'Configuration saved successfully',

                # Analysis Configuration
                'analysis_config': 'Analysis Configuration',
                'analysis_settings': 'Analysis Settings',
                'deep_code_analysis': 'Deep Code Analysis',
                'main_function_call_analysis': 'Main Function Call Analysis',
                'generate_analysis_report': 'Generate Analysis Report',
                'show_call_flowchart': 'Show Call Flowchart',
                'call_depth_setting': 'Call Depth Setting',
                'call_depth_description': 'Set the maximum depth for function call relationship analysis\nGreater depth means more detailed analysis but longer processing time',
                'reset_defaults': 'Reset Defaults',
                'config_saved_success': 'Configuration saved successfully!',
                'save_config_failed': 'Failed to save configuration: {}',

                # Log Messages
                'starting_analysis': 'Starting MCU project analysis...',
                'analysis_completed': 'Analysis completed!',
                'delete_existing_folder': 'Deleting existing analysis folder: {}',
                'delete_existing_file': 'Deleting existing analysis file: {}',
                'cleanup_files_error': 'Error cleaning up existing files: {}',
                'file_analysis_failed': 'File analysis failed {}: {}',
                'parse_function_calls_failed': 'Failed to parse function calls {}: {}',
                'build_call_tree_completed': 'Call tree construction completed, depth: {}',
                'call_tree_function_count': 'Functions in call tree: {}',
                'report_saved': 'Report saved: {}',
                'auto_trigger_flowchart_redraw': 'Auto-triggering flowchart redraw after analysis completion',

                # LLM Analysis
                'llm_analysis_title': 'LLM Analysis',
                'llm_code_analysis': 'LLM Code Analysis',
                'start_llm_analysis': 'Starting LLM intelligent analysis...',
                'llm_analysis_status': 'Performing LLM analysis...',
                'calling_llm': 'Calling LLM...',
                'check_llm_availability': 'Checking LLM service availability...',
                'no_available_llm': 'No available LLM service. Available providers: {}',
                'llm_service_available': 'LLM service available, current provider: {}',
                'start_llm_analysis_process': 'Starting LLM analysis...',
                'llm_analysis_completed': 'LLM analysis completed',
                'llm_call_failed': 'LLM call failed: {}',
                'using_builtin_engine': 'Using built-in analysis engine...',
                'builtin_analysis_completed': 'Built-in analysis completed',
                'llm_analysis_failed': 'LLM analysis failed: {}',

                # Simple LLM Config
                'llm_service_config': 'LLM Service Configuration',
                'select_llm_service': 'Select LLM Service',
                'ollama_local': 'Ollama (Local)',
                'tencent_cloud': 'Tencent Cloud',
                'service_address': 'Service Address:',
                'model_name': 'Model Name:',
                'api_id': 'API ID:',
                'api_secret': 'API Secret:',
                'config_description': 'Configuration Description:\n• Ollama: Free local service, only needs service address and model name\n• Tencent Cloud: Requires API ID and API Secret',
                'test_connection': 'Test Connection',
                'connection_test_developing': 'Connection test feature is under development...',
                'llm_config_saved': 'LLM configuration saved!\nNote: This is simplified configuration mode',

                # Mermaid Source
                'mermaid_source_title': 'Mermaid Source Code',
                'copy_to_clipboard': 'Copy to Clipboard',
                'close': 'Close',
                'mermaid_copied': 'Mermaid source code copied to clipboard',
                'show_source_failed': 'Failed to show source code: {}',
                'please_analyze_first': 'Please run analysis and generate flowchart first',

                # Export Mermaid
                'export_mermaid_flowchart': 'Export Mermaid Flowchart',
                'mermaid_file': 'Mermaid File',
                'svg_vector': 'SVG Vector',
                'png_image': 'PNG Image',
                'html_file': 'HTML File',
                'text_file': 'Text File',
                'all_files': 'All Files',
                'mermaid_source_exported': 'Mermaid source code exported to:\n{}',
                'html_exported': 'HTML file exported to:\n{}',
                'image_exported': '{} image exported to:\n{}',
                'export_image_failed': 'Cannot export {} format directly, saved Mermaid source to:\n{}\n\nYou can use local mermaid-cli tool to convert .mmd file to image format',
                'file_exported': 'File exported to:\n{}',
                'export_failed': 'Export failed: {}',

                # Help and Documentation
                'readme_title': 'README',
                'document_opened': 'README document opened: {}',
                'document_not_found': 'PDF document not found, resource path: {}',
                'meipass_directory': 'MEIPASS directory: {}',
                'current_working_directory': 'Current working directory: {}',
                'open_document_failed': 'Failed to open document: {}',
                'quick_start_help': 'Quick Start: Select project directory → Configure options → Start analysis\n\nSupported formats: Keil/CMake/Makefile/General C++ projects\nLLM Configuration: Config → LLM Config',

                # Application
                'application_closing': 'Application is closing...',
                'close_application_error': 'Error closing application: {}',

                # Analysis Process Messages
                'scanning_project_files': 'Scanning project files...',
                'detecting_chip_info': 'Detecting chip information...',
                'analyzing_code_structure': 'Analyzing code structure...',
                'analyzing_call_relationships': 'Analyzing call relationships...',
                'generating_call_flowchart': 'Generating call flowchart...',
                'generating_analysis_report': 'Generating analysis report...',
                'found_keil_projects': 'Found KEIL project files: {} files',
                'detected_chip_from_keil': 'Detected chip from Keil project file: {}',
                'found_functions_count': 'Found functions: {} functions',
                'main_function_status': 'main function: {}',
                'found_yes': 'Found',
                'not_found': 'Not found',
                'includes_count': 'Include files: {} files',
                'call_tree_depth': 'Call tree depth: {}',
                'functions_in_call_tree': 'Functions in call tree: {}',

                # Configuration Dialog
                'analysis_configuration': 'Analysis Configuration',
                'call_depth_label': 'Call Depth:',
                'save_configuration': 'Save Configuration',
                'configuration_saved_successfully': 'Configuration saved successfully!',
                'failed_to_save_configuration': 'Failed to save configuration: {}',

                # Simple Analysis Report
                'mcu_project_analysis_report': 'MCU Project Intelligent Analysis Report',
                'project_overview': 'Project Overview',
                'project_path': 'Project Path',
                'chip_model': 'Chip Model',
                'chip_vendor': 'Chip Vendor',
                'processor_core': 'Processor Core',
                'code_structure_analysis': 'Code Structure Analysis',
                'total_functions': 'Total Functions',
                'main_function_found': 'Main Function Found',
                'main_function_not_found': 'Main Function Not Found',
                'include_files_count': 'Include Files Count',
                'interface_usage_evaluation': 'Interface Usage Evaluation',
                'detected_interface_usage': 'Detected the following interface usage:',
                'no_obvious_interface_usage': 'No obvious interface usage detected',
                'technical_architecture_evaluation': 'Technical Architecture Evaluation',
                'code_organization': 'Code Organization',
                'interface_usage_characteristics': 'Interface Usage Characteristics',
                'optimization_suggestions': 'Optimization Suggestions',
                'code_quality': 'Code Quality',
                'performance_optimization': 'Performance Optimization',
                'porting_suggestions': 'Porting Suggestions',
                'summary': 'Summary',
                'analysis_generated_by_builtin': 'This analysis was generated by MCU Project Analyzer built-in engine',
                'for_detailed_ai_analysis': 'For more detailed AI analysis, please configure LLM service',

                # File cleanup messages
                'delete_existing_folder': 'Deleting existing analysis folder: {}',
                'delete_existing_file': 'Deleting existing analysis file: {}',

                # LLM Analysis Dialog
                'please_complete_analysis_first': 'Please complete project analysis first',
                'no_analysis_results': 'No analysis results available, please run project analysis first',
                'warning': 'Warning',

                # Common UI Text
                'unknown': 'Unknown',
                'success': 'Success',
                'failed': 'Failed',
                'completed': 'Completed',
                'processing': 'Processing',
                'ready': 'Ready',
                'cleared': 'Cleared',

                # File and Directory Operations
                'document_opened': 'Document opened: {}',
                'document_not_found': 'PDF document not found, resource path: {}',
                'meipass_directory': 'MEIPASS directory: {}',
                'current_working_directory': 'Current working directory: {}',
                'open_document_failed': 'Failed to open document: {}',
                'cleanup_files_error': 'Error cleaning up existing files: {}',

                # Analysis Process
                'starting_analysis': 'Starting MCU project analysis...',
                'analysis_completed': 'Analysis completed!',
                'auto_trigger_flowchart_redraw': 'Auto-triggering flowchart redraw after analysis completion',

                # Debug Messages
                'creating_analyze_button': 'Creating analyze button...',
                'analyze_button_created': 'Analyze button created successfully!',
                'llm_analysis_button_created': 'LLM analysis button created successfully!',
                'loaded_last_project_path': 'Loaded last project path: {}',
                'start_analysis_called': 'start_analysis() called!',
                'project_path_equals': 'project_path = {}',
                'output_path_equals': 'output_path = {}',
                'all_paths_validated': 'All paths validated, starting analysis...',
                'cleaning_existing_folders': 'Cleaning existing analysis folders...',
                'starting_analysis_thread': 'Starting analysis thread...',
                'run_analysis_started': 'run_analysis() started!',
                'analysis_thread_started': 'Analysis thread started!',
                'about_to_call_log_message': 'About to call log_message...',
                'log_message_called_successfully': 'log_message called successfully',
                'about_to_update_status': 'About to update status...',
                'status_updated_successfully': 'Status updated successfully',
                'about_to_update_progress': 'About to update progress...',
                'progress_updated_successfully': 'Progress updated successfully',

                # Configuration and Settings
                'load_analysis_config_failed': 'Failed to load analysis config: {}',
                'configuration_saved_successfully': 'Configuration saved successfully!',
                'failed_to_save_configuration': 'Failed to save configuration: {}',
                'llm_config_saved': 'LLM configuration saved! Note: This is simplified configuration mode',
                'connection_test_developing': 'Connection test feature is under development...',

                # Interface Analysis
                'detected_interfaces': 'Detected interfaces: {}',
                'interface_usage_statistics': 'Interface Usage Statistics:',
                'no_interface_usage_detected': 'No obvious interface usage detected',

                # Mermaid and Flowchart
                'mermaid_source_title': 'Mermaid Source Code',
                'copy_to_clipboard': 'Copy to Clipboard',
                'mermaid_copied': 'Mermaid source code copied to clipboard',
                'show_source_failed': 'Failed to show source code: {}',
                'please_analyze_first': 'Please run analysis and generate flowchart first',
                'export_mermaid_flowchart': 'Export Mermaid Flowchart',
                'mermaid_file': 'Mermaid File',
                'svg_vector': 'SVG Vector',
                'png_image': 'PNG Image',
                'html_file': 'HTML File',
                'text_file': 'Text File',
                'all_files': 'All Files',
                'mermaid_source_exported': 'Mermaid source code exported to: {}',
                'html_exported': 'HTML file exported to: {}',
                'image_exported': '{} image exported to: {}',
                'export_image_failed': 'Cannot export {} format directly, saved Mermaid source to: {}\n\nYou can use local mermaid-cli tool to convert .mmd file to image format',
                'file_exported': 'File exported to: {}',
                'export_failed': 'Export failed: {}',

                # Help and Documentation
                'quick_start': 'Quick Start:',
                'select_project_directory': 'Select MCU project directory',
                'configure_analysis_options': 'Configure analysis options',
                'click_start_analysis': 'Click "Start Analysis"',
                'view_analysis_results': 'View analysis results',
                'supported_project_types': 'Supported Project Types:',
                'keil_uvision_projects': 'Keil uVision projects (.uvprojx, .uvproj)',
                'cmake_projects': 'CMake projects (CMakeLists.txt)',
                'makefile_projects': 'Makefile projects',
                'general_cpp_projects': 'General C/C++ projects',
                'llm_configuration': 'LLM Configuration:',
                'supports_ollama_local': 'Supports Ollama local models',
                'supports_tencent_cloud': 'Supports Tencent Cloud API',
                'config_llm_config': 'Config → LLM Config for configuration',
                'complete_documentation': 'Complete Documentation: MCU_Code_Analyzer_Complete_Documentation.pdf',
                'quick_start_simple': 'Quick Start: Select project directory → Configure options → Start analysis',
                'supported_formats': 'Supported formats: Keil/CMake/Makefile/General C++ projects',

                # Error Messages and Warnings
                'application_closing': 'Application is closing...',
                'close_application_error': 'Error closing application: {}',
                'graph_status_label_destroyed': 'graph_status_label has been destroyed, cannot update status',
                'graph_display_cleared': 'Graph display cleared',
                'failed_to_set_progress_color': 'Failed to set progress color: {}',
                'llm_analysis_start_failed': 'LLM analysis start failed: {}',
                'startup_llm_analysis_failed': 'Failed to start LLM analysis: {}',
                'start_analysis_called': 'start_analysis() called!',
                'output_path_equals': 'output_path = {}',

                # Analysis Configuration and Settings
                'analysis_configuration': 'Analysis Configuration',
                'analysis_options': 'Analysis Options',
                'deep_code_analysis': 'Deep Code Analysis',
                'main_function_call_analysis': 'Main Function Call Analysis',
                'generate_analysis_report': 'Generate Analysis Report',
                'show_call_flowchart': 'Show Call Flowchart',
                'call_depth_setting': 'Call Depth Setting',
                'call_depth_label': 'Call Depth:',
                'call_depth_description': 'Set the maximum depth for function call relationship analysis\nGreater depth means more detailed analysis but longer processing time',
                'reset_defaults': 'Reset Defaults',
                'save_configuration': 'Save Configuration',

                # LLM Configuration
                'llm_service_configuration': 'LLM Service Configuration',
                'select_llm_service': 'Select LLM Service',
                'ollama_local': 'Ollama (Local)',
                'tencent_cloud': 'Tencent Cloud',
                'service_address': 'Service Address:',
                'model_name': 'Model Name:',
                'api_id': 'API ID:',
                'api_secret': 'API Secret:',
                'config_description': 'Configuration Description:\n• Ollama: Free local service, only needs service address and model name\n• Tencent Cloud: Requires API ID and API Secret',
                'test_connection': 'Test Connection',

                # Analysis Process Messages
                'skip_directories': 'Skipping directories',
                'found_source_files': 'Found source files: {} files',
                'found_header_files': 'Found header files: {} files',
                'found_project_files': 'Found project files: {} files',
                'analyzing_code_structure': 'Analyzing code structure...',
                'analyzing_call_relationships': 'Analyzing call relationships...',
                'generating_call_flowchart': 'Generating call flowchart...',
                'generating_analysis_report': 'Generating analysis report...',
                'parsing_function_definitions_and_calls': 'Parsing function definitions and calls...',
                'building_call_tree': 'Building call tree...',
                'call_tree_construction_completed': 'Call tree construction completed',
                'functions_in_call_tree': 'Functions in call tree: {}',
                'call_tree_depth': 'Call tree depth: {}',

                # File Analysis
                'analyzing_file': 'Analyzing file: {}',
                'found_functions': 'Found functions: {}',
                'found_includes': 'Found includes: {}',
                'main_function_found': 'Main function found',
                'main_function_not_found': 'Main function not found',
                'includes_count': 'Include files: {} files',

                # Interface Detection
                'interface_patterns': 'Interface patterns',
                'gpio_interface': 'GPIO',
                'uart_interface': 'UART',
                'spi_interface': 'SPI',
                'i2c_interface': 'I2C',
                'timer_interface': 'Timer',
                'adc_interface': 'ADC',
                'dac_interface': 'DAC',
                'pwm_interface': 'PWM',
                'can_interface': 'CAN',
                'usb_interface': 'USB',
                'ethernet_interface': 'Ethernet',
                'dma_interface': 'DMA',

                # Mermaid Generation
                'no_call_relationships_found': 'No call relationships found',
                'no_main_function_or_call_relationships': 'No main function or call relationships found',
                'adaptive_layout_description': 'Adaptive layout description:',
                'ui_width': 'UI width: {}px, nodes per row: {}',
                'red_main_function': '🔴 Red: main function (program entry)',
                'green_hal_functions': '🟢 Green: HAL/interface functions',
                'blue_user_functions': '🔵 Blue: user-defined functions',
                'hierarchical_flowchart_description': 'Hierarchical flowchart description:',
                'yellow_green_second_layer': '🟡 Yellow-green: second layer user functions',
                'yellow_deeper_functions': '🟡 Yellow: deeper layer functions',
                'interface_usage_statistics_comment': 'Interface usage statistics',
                'times_called': 'times called',

                # File scanning and analysis
                'skip_directories': 'Skipping directories',
                'analyzing_file': 'Analyzing file: {}',
                'found_functions': 'Found functions: {}',
                'found_includes': 'Found includes: {}',
                'main_function_found': 'Main function found',
                'main_function_not_found': 'Main function not found',
                'includes_count': 'Include files: {} files',
                'parsing_function_definitions_and_calls': 'Parsing function definitions and calls...',
                'building_call_tree': 'Building call tree...',
                'call_tree_construction_completed': 'Call tree construction completed',
                'functions_in_call_tree': 'Functions in call tree: {}',
                'call_tree_depth': 'Call tree depth: {}',

                # Comments and descriptions
                'graph_rendering_related': 'Graph rendering related',
                'safe_json_serialization': 'Safe JSON serialization function, handles non-serializable types like set',
                'config_file_path_hidden': 'Configuration file path (hidden file in exe directory)',
                'add_canvas_rounded_rect': 'Add Canvas rounded rectangle method',
                'load_last_config': 'Load last configuration',
                'analysis_results_ensure_defaults': 'Analysis results - ensure all attributes have default values',
                'config_dialog_already_shown': 'ConfigDialog already shown in __init__, no need to call show()',
                'find_pdf_document': 'Find PDF document file',
                'get_resource_file_path': 'Get resource file path',
                'get_absolute_path_resource': 'Get absolute path of resource file',
                'if_packaged_exe_temp_dir': 'If packaged exe file, resources are in temp directory',
                'if_python_script_dir': 'If Python script, resources are in script directory',
                'try_get_pdf_from_package': 'Try to get PDF from packaged resources',
                'if_not_in_package_try_other': 'If not in packaged resources, try other locations',
                'get_exe_directory': 'Get exe file directory',
                'search_path_list': 'Search path list',
                'exe_directory': 'exe file directory',
                'current_working_dir': 'current working directory',
                'parent_directory': 'parent directory',
                'exe_parent_directory': 'exe directory parent directory',
                'open_document_by_os': 'Open document by operating system',
                'if_no_document_show_help': 'If document not found, show simplified help',
                'quick_start_colon': 'Quick Start:',
                'select_mcu_project_dir': 'Select MCU project directory',
                'configure_analysis_opts': 'Configure analysis options',
                'click_start_analysis': 'Click "Start Analysis"',
                'view_analysis_results': 'View analysis results',
                'supported_project_types_colon': 'Supported Project Types:',
                'keil_uvision_projects_ext': 'Keil uVision projects (.uvprojx, .uvproj)',
                'cmake_projects_ext': 'CMake projects (CMakeLists.txt)',
                'makefile_projects_simple': 'Makefile projects',
                'general_cpp_projects_simple': 'General C/C++ projects',
                'llm_configuration_colon': 'LLM Configuration:',
                'supports_ollama_local_models': 'Supports Ollama local models',
                'supports_tencent_cloud_api': 'Supports Tencent Cloud API',
                'config_llm_config_path': 'Config → LLM Config for configuration',
                'complete_documentation_pdf': 'Complete Documentation: MCU_Code_Analyzer_Complete_Documentation.pdf',
                'fallback_to_simple_help': 'Fallback to simplified help',
                'quick_start_simple_flow': 'Quick Start: Select project directory → Configure options → Start analysis',
                'supported_formats_list': 'Supported formats: Keil/CMake/Makefile/General C++ projects',
                'llm_config_path_simple': 'LLM Configuration: Config → LLM Config',

                # Analysis process details
                'skip_some_directories': 'Skip some directories',
                'limit_analysis_file_count': 'Limit analysis file count',
                'find_functions': 'Find functions',
                'find_include_files': 'Find include files',
                'change_to_list_not_set': 'Change to list instead of set',
                'get_call_depth_from_config': 'Get call depth from configuration file',
                'store_all_function_definitions_calls': 'Store all function definitions and calls',
                'first_step': 'First step',
                'parse_all_function_definitions': 'Parse all function definitions',
                'remove_comments_string_literals': 'Remove comments and string literals',
                'avoid_misidentification': 'Avoid misidentification',
                'find_function_definitions': 'Find function definitions',
                'second_step': 'Second step',
                'analyze_function_call_relationships': 'Analyze function call relationships',
                'analyze_internal_function_calls': 'Analyze internal function call relationships',
                'build_call_tree_from_main': 'Build call tree starting from main function',
                'third_step': 'Third step',
                'analyze_interface_usage': 'Analyze interface usage',
                'only_count_functions_in_call_tree': 'Only count functions in call tree',
                'save_to_instance_for_mermaid': 'Save to instance variables for Mermaid use',
                'save_interface_info_for_llm': 'Save interface usage information for LLM use',

                # Code processing and analysis
                'remove_c_comments_strings': 'Remove comments and string literals from C code',
                'simplified_version': 'Simplified version',
                'remove_single_line_comments': 'Remove single line comments',
                'remove_multi_line_comments': 'Remove multi line comments',
                'remove_string_literals': 'Remove string literals',
                'extract_function_definitions': 'Extract function definitions',
                'regex_for_function_definitions': 'Regular expression for matching function definitions',
                'exclude_some_keywords': 'Exclude some keywords',
                'extract_function_calls': 'Extract function calls',
                'regex_for_function_calls': 'Regular expression for matching function calls',
                'exclude_keywords_non_function_calls': 'Exclude keywords and common non-function calls',
                'find_all_function_positions_content': 'Find all function definition positions and content in file',
                'find_function_body_start': 'Find function body start position',
                'function_body_start': 'Function body start',
                'find_matching_closing_brace': 'Find matching closing brace',
                'find_function_calls_in_body': 'Find function calls in function body',
                'keep_only_defined_function_calls': 'Keep only function calls defined in all_functions',
                'avoid_self_calls': 'Avoid self calls',
                'update_function_call_list': 'Update function call list',
                'remove_duplicates': 'Remove duplicates',
                'extract_function_body_content': 'Extract function body content',
                'from_start_brace_to_matching_end': 'From start brace to matching end brace',
                'no_matching_closing_brace_found': 'No matching closing brace found',

                # Call tree construction
                'build_call_tree': 'Build call tree',
                'recursively_build_child_nodes': 'Recursively build child nodes',
                'count_functions_in_call_tree': 'Count functions in call tree',
                'get_max_call_tree_depth': 'Get maximum call tree depth',
                'analyze_interface_usage_in_call_tree': 'Analyze interface usage in call tree',
                'collect_all_function_names_in_call_tree': 'Collect all function names in call tree',
                'interface_patterns': 'Interface patterns',
                'search_interface_usage_in_call_tree_files': 'Search interface usage only in call tree related files',
                'check_if_file_contains_call_tree_functions': 'Check if file contains call tree functions',
                'only_count_function_calls': 'Only count function calls',
                'dont_count_definitions_comments': 'Do not count definitions and comments',
                'only_return_used_interfaces': 'Only return used interfaces',
                'collect_all_function_names_from_call_tree': 'Collect all function names from call tree',
                'interface_keyword_patterns': 'Interface keyword patterns',
                'keep_only_used_interfaces': 'Keep only used interfaces',

                # Function call relationship analysis
                'extract_plain_text_function_call_relationships': 'Extract plain text function call relationships',
                'no_call_relationship_analysis_performed': 'No call relationship analysis performed',
                'no_main_function_call_relationships_found': 'No main function call relationships found',
                'recursively_extract_call_tree_text': 'Recursively extract call tree text representation',
                'unknown_function': 'Unknown function',
                'main_function_program_entry': 'main function (program entry)',
                'recursively_process_child_nodes': 'Recursively process child nodes',
                'format_interface_info_for_prompt_clean': 'Format interface information for prompt (no special characters)',
                'no_interface_usage_detected_clean': 'No interface usage detected',
                'times_called_clean': 'times called',
                'safe_get_chip_info': 'Safe get chip info',
                'mcu_project_analysis_request': 'MCU project analysis request',
                'project_overview': 'Project overview',
                'project_path': 'Project path',
                'chip_model': 'Chip model',
                'chip_vendor': 'Chip vendor',
                'processor_core': 'Processor core',
                'code_structure': 'Code structure',
                'total_function_count': 'Total function count',
                'main_function_status': 'main function',
                'exists': 'exists',
                'not_found': 'not found',
                'include_file_count': 'Include file count',
                'interface_usage': 'Interface usage',
                'function_call_relationships': 'Function call relationships',
                'analyze_based_on_above_info': 'Please analyze based on the above information, generate what specific functions this project implements using chip information, and which chip modules are used.',

                # User prompt template
                'mcu_project_analysis_request_title': 'MCU Project Analysis Request',
                'project_overview_title': 'Project Overview:',
                'project_path_label': 'Project path',
                'chip_model_label': 'Chip model',
                'chip_vendor_label': 'Chip vendor',
                'processor_core_label': 'Processor core',
                'code_structure_title': 'Code Structure:',
                'total_function_count_label': 'Total function count',
                'main_function_label': 'main function',
                'exists_label': 'exists',
                'not_found_label': 'not found',
                'include_file_count_label': 'Include file count',
                'interface_usage_title': 'Interface Usage:',
                'function_call_relationships_title': 'Function Call Relationships:',
                'analyze_request_text': 'Please analyze based on the above information to determine what specific functions this project implements using chip information and which chip modules are used.',

                # LLM Configuration Dialog
                'llm_config': 'LLM Configuration',
                'llm_service_config': 'LLM Service Configuration',
                'select_llm_service': 'Select LLM Service',
                'ollama_local': 'Ollama (Local)',
                'tencent_cloud': 'Tencent Cloud',
                'config_parameters': 'Configuration Parameters',
                'service_address': 'Service Address:',
                'model_name': 'Model Name:',
                'api_id': 'API ID:',
                'api_key': 'API Key:',
                'config_description': 'Configuration Description:',
                'ollama_description': 'Ollama: Local free service, only requires service address and model name',
                'tencent_description': 'Tencent Cloud: Requires API ID and API Key',
                'test_connection': 'Test Connection',
                'save': 'Save',
                'cancel': 'Cancel',
                'llm_config_saved': 'LLM configuration saved!\\nNote: This is simplified configuration mode',
                'connection_test_in_development': 'Connection test feature is under development...',

                # Analysis Configuration Dialog
                'analysis_config': 'Analysis Configuration',
                'analysis_options': 'Analysis Options',
                'deep_code_analysis': 'Deep Code Analysis',
                'main_function_call_analysis': 'main Function Call Analysis',
                'generate_analysis_report': 'Generate Analysis Report',
                'show_call_flowchart': 'Show Call Flowchart',
                'call_depth_settings': 'Call Depth Settings',
                'call_depth': 'Call Depth:',
                'call_depth_description': 'Set the maximum depth for function call relationship analysis\\nGreater depth provides more detailed analysis but takes longer',
                'reset_defaults': 'Reset Defaults',
                'config_saved_successfully': 'Configuration saved successfully!',
                'save_config_failed': 'Failed to save configuration',
            },
            'zh': {
                # Window titles
                'main_title': f'MCU代码分析器 v{self.version}',
                'about_title': '关于',
                'config_title': '配置',
                
                # Menu items
                'menu_config': '配置',
                'menu_llm_config': 'LLM配置',
                'menu_analysis_settings': '分析设置',
                'menu_help': '帮助',
                'menu_usage': 'README',
                'menu_about': '关于',
                
                # Project settings
                'project_settings': '项目设置',
                'project_directory': 'MCU项目目录:',
                'output_directory': '输出目录:',
                'browse': '浏览',
                
                # Analysis options
                'analysis_options': '分析选项',
                'deep_analysis': '✓ 深度代码分析',
                'call_analysis': 'main函数调用分析',
                'generate_report': '生成分析报告',
                'call_depth': '调用深度:',
                'show_flowchart': '显示调用流程图',
                
                # Control buttons
                'start_analysis': '开始分析',
                'llm_analysis': 'LLM分析',
                'clear': '清空',
                'about': '关于',
                
                # Status and progress
                'ready': '就绪',
                'analyzing': '正在分析...',
                'analysis_complete': '分析完成！',
                'analysis_failed': '分析失败',
                
                # Result tabs
                'project_overview': '项目概览',
                'detailed_analysis': '详细分析',
                'call_flowchart': '调用流程图',
                'execution_log': '执行日志',
                
                # Flowchart controls
                'refresh_flowchart': '刷新流程图',
                'render_graphics': '渲染图形',
                'export_code': '导出代码',
                'mermaid_source': 'Mermaid源码',
                'graphics_preview': '图形预览',
                'render_graph': '渲染图形',
                'clear_graph': '清空图形',
                
                # Messages
                'select_project_dir': '请选择MCU项目目录',
                'select_output_dir': '请选择输出目录',
                'project_dir_not_exist': '项目目录不存在',
                'analysis_complete_msg': '分析完成！\n结果已保存到: {}',
                'no_flowchart': '没有可渲染的流程图，请先进行调用关系分析',
                'no_mermaid_code': '没有可导出的流程图',
                'save_mermaid_code': '保存Mermaid代码',
                'mermaid_saved': 'Mermaid代码已保存到:\n{}',
                'save_failed': '保存失败:\n{}',
                'render_failed': '渲染失败:\n{}',
                
                # File scanning
                'scanning_files': '扫描项目文件...',
                'detecting_chip': '识别芯片信息...',
                'analyzing_code': '分析代码结构...',
                'analyzing_calls': '分析调用关系...',
                'generating_flowchart': '生成调用流程图...',
                'generating_report': '生成分析报告...',
                
                # Statistics
                'found_source_files': '找到源文件: {} 个',
                'found_header_files': '找到头文件: {} 个',
                'found_project_files': '找到项目文件: {} 个',
                'found_functions': '找到函数: {} 个',
                'main_function': 'main函数',
                'detected_chip': '检测到芯片: {}',
                'detected_interfaces': '检测到接口: {}',
                
                # Chip info
                'unknown': '未知',
                'device': '设备',
                'vendor': '厂商',
                'series': '系列',
                'core': '内核',
                
                # About dialog
                'about_text': f'''MCU代码分析器 v{self.version}

专业的MCU项目代码分析工具

功能特性:
• 智能芯片识别
• 代码流程图生成
• LLM智能分析
• 多线程处理
• 专业UI界面

开发团队: AI Assistant
技术支持: 基于Claude AI''',
                
                # Error messages
                'error': '错误',
                'warning': '警告',
                'info': '信息',
                'success': '成功',
                'failed': '失败',
                'cleanup_error': '清理已有文件时出错: {}',
                'parse_error': '解析项目文件失败: {}',
                'analysis_error': '分析失败: {}',
                'file_analysis_error': '分析文件失败 {}: {}',
                
                # Language settings
                'language': '语言',
                'english': 'English',
                'chinese': '中文',

                # LLM Configuration
                'llm_config': 'LLM配置',
                'select_llm_provider': '选择LLM提供商',
                'config_params': '配置参数',
                'save': '保存',
                'cancel': '取消',
                'config_saved': '配置保存成功',

                # Analysis Configuration
                'analysis_config': '分析配置',
                'analysis_settings': '分析设置',
                'deep_code_analysis': '深度代码分析',
                'main_function_call_analysis': 'main函数调用分析',
                'generate_analysis_report': '生成分析报告',
                'show_call_flowchart': '显示调用流程图',
                'call_depth_setting': '调用深度设置',
                'call_depth_description': '设置函数调用关系分析的最大深度\n深度越大，分析越详细，但耗时更长',
                'reset_defaults': '重置默认',
                'config_saved_success': '配置已保存成功！',
                'save_config_failed': '保存配置失败: {}',

                # Log Messages
                'starting_analysis': '开始MCU项目分析...',
                'analysis_completed': '分析完成！',
                'delete_existing_folder': '删除已有分析文件夹: {}',
                'delete_existing_file': '删除已有分析文件: {}',
                'cleanup_files_error': '清理已有文件时出错: {}',
                'file_analysis_failed': '分析文件失败 {}: {}',
                'parse_function_calls_failed': '解析调用关系失败 {}: {}',
                'build_call_tree_completed': '构建调用树完成，深度: {}',
                'call_tree_function_count': '调用树中函数数量: {}',
                'report_saved': '报告已保存: {}',
                'auto_trigger_flowchart_redraw': '分析完成后自动触发流程图重绘',

                # LLM Analysis
                'llm_analysis_title': 'LLM分析',
                'llm_code_analysis': 'LLM代码分析',
                'start_llm_analysis': '开始LLM智能分析...',
                'llm_analysis_status': '正在进行LLM分析...',
                'calling_llm': '正在调用LLM...',
                'check_llm_availability': '检查LLM服务可用性...',
                'no_available_llm': '没有可用的LLM服务。可用提供商: {}',
                'llm_service_available': 'LLM服务可用，当前提供商: {}',
                'start_llm_analysis_process': '开始LLM分析...',
                'llm_analysis_completed': 'LLM分析完成',
                'llm_call_failed': 'LLM call failed: {}',
                'using_builtin_engine': '使用内置分析引擎...',
                'builtin_analysis_completed': '内置分析完成',
                'llm_analysis_failed': 'LLM分析失败: {}',

                # Simple LLM Config
                'llm_service_config': 'LLM服务配置',
                'select_llm_service': '选择LLM服务',
                'ollama_local': 'Ollama (本地)',
                'tencent_cloud': '腾讯云',
                'service_address': '服务地址:',
                'model_name': '模型名称:',
                'api_id': 'API ID:',
                'api_secret': 'API密钥:',
                'config_description': '配置说明：\n• Ollama: 本地免费服务，只需服务地址和模型名称\n• 腾讯云: 需要API ID和API密钥',
                'test_connection': '测试连接',
                'connection_test_developing': '连接测试功能正在开发中...',
                'llm_config_saved': 'LLM配置已保存！\n注意：当前为简化配置模式',

                # Mermaid Source
                'mermaid_source_title': 'Mermaid源码',
                'copy_to_clipboard': '复制到剪贴板',
                'close': '关闭',
                'mermaid_copied': 'Mermaid源码已复制到剪贴板',
                'show_source_failed': '显示源码失败: {}',
                'please_analyze_first': '请先进行分析并生成流程图',

                # Export Mermaid
                'export_mermaid_flowchart': '导出Mermaid流程图',
                'mermaid_file': 'Mermaid文件',
                'svg_vector': 'SVG矢量图',
                'png_image': 'PNG图片',
                'html_file': 'HTML文件',
                'text_file': '文本文件',
                'all_files': '所有文件',
                'mermaid_source_exported': 'Mermaid源码已导出到:\n{}',
                'html_exported': 'HTML文件已导出到:\n{}',
                'image_exported': '{}图片已导出到:\n{}',
                'export_image_failed': '无法直接导出{}格式，已保存Mermaid源码到:\n{}\n\n您可以使用本地mermaid-cli工具将.mmd文件转换为图片格式',
                'file_exported': '文件已导出到:\n{}',
                'export_failed': '导出失败: {}',

                # Help and Documentation
                'readme_title': 'README',
                'document_opened': '已打开README文档: {}',
                'document_not_found': '未找到PDF文档，资源路径: {}',
                'meipass_directory': 'MEIPASS目录: {}',
                'current_working_directory': '当前工作目录: {}',
                'open_document_failed': '打开文档失败: {}',
                'quick_start_help': '快速开始：选择项目目录 → 配置选项 → 开始分析\n\n支持格式：Keil/CMake/Makefile/通用C++项目\nLLM配置：Config → LLM Config',

                # Application
                'application_closing': '应用程序正在关闭...',
                'close_application_error': '关闭应用程序时出错: {}',

                # Analysis Process Messages
                'scanning_project_files': '扫描项目文件...',
                'detecting_chip_info': '检测芯片信息...',
                'analyzing_code_structure': '分析代码结构...',
                'analyzing_call_relationships': '分析调用关系...',
                'generating_call_flowchart': '生成调用流程图...',
                'generating_analysis_report': '生成分析报告...',
                'found_keil_projects': '找到 KEIL 项目文件: {} 个',
                'detected_chip_from_keil': '从Keil项目文件检测到芯片: {}',
                'found_functions_count': '找到函数: {} 个',
                'main_function_status': 'main函数: {}',
                'found_yes': '已找到',
                'not_found': '未找到',
                'includes_count': '包含文件: {} 个',
                'call_tree_depth': '调用树深度: {}',
                'functions_in_call_tree': '调用树中函数数量: {}',

                # Configuration Dialog
                'analysis_configuration': '分析配置',
                'call_depth_label': '调用深度:',
                'save_configuration': '保存配置',
                'configuration_saved_successfully': '配置已保存成功！',
                'failed_to_save_configuration': '保存配置失败: {}',

                # Simple Analysis Report
                'mcu_project_analysis_report': 'MCU项目智能分析报告',
                'project_overview': '项目概述',
                'project_path': '项目路径',
                'chip_model': '芯片型号',
                'chip_vendor': '芯片厂商',
                'processor_core': '处理器内核',
                'code_structure_analysis': '代码结构分析',
                'total_functions': '总函数数量',
                'main_function_found': '已找到main函数',
                'main_function_not_found': '未找到main函数',
                'include_files_count': '包含文件数',
                'interface_usage_evaluation': '接口使用评估',
                'detected_interface_usage': '检测到以下接口使用：',
                'no_obvious_interface_usage': '未检测到明显的接口使用',
                'technical_architecture_evaluation': '技术架构评估',
                'code_organization': '代码组织',
                'interface_usage_characteristics': '接口使用特点',
                'optimization_suggestions': '优化建议',
                'code_quality': '代码质量',
                'performance_optimization': '性能优化',
                'porting_suggestions': '移植建议',
                'summary': '总结',
                'analysis_generated_by_builtin': '本分析由MCU工程分析器内置引擎生成',
                'for_detailed_ai_analysis': '如需更详细的AI分析，请配置LLM服务',

                # File cleanup messages
                'delete_existing_folder': '删除已有分析文件夹: {}',
                'delete_existing_file': '删除已有分析文件: {}',

                # LLM Analysis Dialog
                'please_complete_analysis_first': '请先完成项目分析',
                'no_analysis_results': '没有可用的分析结果，请先运行项目分析',
                'warning': '警告',

                # Common UI Text
                'unknown': '未知',
                'success': '成功',
                'failed': '失败',
                'completed': '完成',
                'processing': '处理中',
                'ready': '就绪',
                'cleared': '已清空',

                # File and Directory Operations
                'document_opened': '已打开文档: {}',
                'document_not_found': '未找到PDF文档，资源路径: {}',
                'meipass_directory': 'MEIPASS目录: {}',
                'current_working_directory': '当前工作目录: {}',
                'open_document_failed': '打开文档失败: {}',
                'cleanup_files_error': '清理已有文件时出错: {}',

                # Analysis Process
                'starting_analysis': '开始MCU项目分析...',
                'analysis_completed': '分析完成！',
                'auto_trigger_flowchart_redraw': '分析完成后自动触发流程图重绘',

                # Debug Messages
                'creating_analyze_button': '正在创建分析按钮...',
                'analyze_button_created': '分析按钮创建成功！',
                'llm_analysis_button_created': 'LLM分析按钮创建成功！',
                'loaded_last_project_path': '已加载上次项目路径: {}',
                'start_analysis_called': 'start_analysis() 已调用！',
                'project_path_equals': '项目路径 = {}',
                'output_path_equals': '输出路径 = {}',
                'all_paths_validated': '所有路径已验证，开始分析...',
                'cleaning_existing_folders': '正在清理已有分析文件夹...',
                'starting_analysis_thread': '正在启动分析线程...',
                'run_analysis_started': 'run_analysis() 已启动！',
                'analysis_thread_started': '分析线程已启动！',
                'about_to_call_log_message': '即将调用log_message...',
                'log_message_called_successfully': 'log_message调用成功',
                'about_to_update_status': '即将更新状态...',
                'status_updated_successfully': '状态更新成功',
                'about_to_update_progress': '即将更新进度...',
                'progress_updated_successfully': '进度更新成功',

                # Configuration and Settings
                'load_analysis_config_failed': '加载分析配置失败: {}',
                'configuration_saved_successfully': '配置已保存成功！',
                'failed_to_save_configuration': '保存配置失败: {}',
                'llm_config_saved': 'LLM配置已保存！注意：当前为简化配置模式',
                'connection_test_developing': '连接测试功能正在开发中...',

                # Interface Analysis
                'detected_interfaces': '检测到接口: {}',
                'interface_usage_statistics': '接口使用统计:',
                'no_interface_usage_detected': '未检测到明显的接口使用',

                # Mermaid and Flowchart
                'mermaid_source_title': 'Mermaid源码',
                'copy_to_clipboard': '复制到剪贴板',
                'mermaid_copied': 'Mermaid源码已复制到剪贴板',
                'show_source_failed': '显示源码失败: {}',
                'please_analyze_first': '请先进行分析并生成流程图',
                'export_mermaid_flowchart': '导出Mermaid流程图',
                'mermaid_file': 'Mermaid文件',
                'svg_vector': 'SVG矢量图',
                'png_image': 'PNG图片',
                'html_file': 'HTML文件',
                'text_file': '文本文件',
                'all_files': '所有文件',
                'mermaid_source_exported': 'Mermaid源码已导出到: {}',
                'html_exported': 'HTML文件已导出到: {}',
                'image_exported': '{}图片已导出到: {}',
                'export_image_failed': '无法直接导出{}格式，已保存Mermaid源码到: {}\n\n您可以使用本地mermaid-cli工具将.mmd文件转换为图片格式',
                'file_exported': '文件已导出到: {}',
                'export_failed': '导出失败: {}',

                # Help and Documentation
                'quick_start': '快速开始：',
                'select_project_directory': '选择MCU项目目录',
                'configure_analysis_options': '配置分析选项',
                'click_start_analysis': '点击"开始分析"',
                'view_analysis_results': '查看分析结果',
                'supported_project_types': '支持的项目类型：',
                'keil_uvision_projects': 'Keil uVision项目 (.uvprojx, .uvproj)',
                'cmake_projects': 'CMake项目 (CMakeLists.txt)',
                'makefile_projects': 'Makefile项目',
                'general_cpp_projects': '通用C/C++项目',
                'llm_configuration': 'LLM配置：',
                'supports_ollama_local': '支持Ollama本地模型',
                'supports_tencent_cloud': '支持腾讯云API',
                'config_llm_config': 'Config → LLM Config 进行配置',
                'complete_documentation': '完整文档：MCU_Code_Analyzer_Complete_Documentation.pdf',
                'quick_start_simple': '快速开始：选择项目目录 → 配置选项 → 开始分析',
                'supported_formats': '支持格式：Keil/CMake/Makefile/通用C++项目',

                # Error Messages and Warnings
                'application_closing': '应用程序正在关闭...',
                'close_application_error': '关闭应用程序时出错: {}',
                'graph_status_label_destroyed': 'graph_status_label已被销毁，无法更新状态',
                'graph_display_cleared': '图形显示已清空',
                'failed_to_set_progress_color': '设置进度条颜色失败: {}',
                'llm_analysis_start_failed': 'LLM分析启动失败: {}',
                'startup_llm_analysis_failed': '启动LLM分析失败: {}',
                'start_analysis_called': 'start_analysis() 已调用！',
                'output_path_equals': '输出路径 = {}',

                # Analysis Configuration and Settings
                'analysis_configuration': '分析配置',
                'analysis_options': '分析选项',
                'deep_code_analysis': '深度代码分析',
                'main_function_call_analysis': 'main函数调用分析',
                'generate_analysis_report': '生成分析报告',
                'show_call_flowchart': '显示调用流程图',
                'call_depth_setting': '调用深度设置',
                'call_depth_label': '调用深度:',
                'call_depth_description': '设置函数调用关系分析的最大深度\n深度越大，分析越详细，但耗时更长',
                'reset_defaults': '重置默认',
                'save_configuration': '保存配置',

                # LLM Configuration
                'llm_service_configuration': 'LLM服务配置',
                'select_llm_service': '选择LLM服务',
                'ollama_local': 'Ollama (本地)',
                'tencent_cloud': '腾讯云',
                'service_address': '服务地址:',
                'model_name': '模型名称:',
                'api_id': 'API ID:',
                'api_secret': 'API密钥:',
                'config_description': '配置说明：\n• Ollama: 本地免费服务，只需服务地址和模型名称\n• 腾讯云: 需要API ID和API密钥',
                'test_connection': '测试连接',

                # Analysis Process Messages
                'skip_directories': '跳过目录',
                'found_source_files': '找到源文件: {} 个',
                'found_header_files': '找到头文件: {} 个',
                'found_project_files': '找到项目文件: {} 个',
                'analyzing_code_structure': '分析代码结构...',
                'analyzing_call_relationships': '分析调用关系...',
                'generating_call_flowchart': '生成调用流程图...',
                'generating_analysis_report': '生成分析报告...',
                'parsing_function_definitions_and_calls': '解析函数定义和调用...',
                'building_call_tree': '构建调用树...',
                'call_tree_construction_completed': '调用树构建完成',
                'functions_in_call_tree': '调用树中函数数量: {}',
                'call_tree_depth': '调用树深度: {}',

                # File Analysis
                'analyzing_file': '分析文件: {}',
                'found_functions': '找到函数: {}',
                'found_includes': '找到包含文件: {}',
                'main_function_found': '找到main函数',
                'main_function_not_found': '未找到main函数',
                'includes_count': '包含文件: {} 个',

                # Interface Detection
                'interface_patterns': '接口模式',
                'gpio_interface': 'GPIO',
                'uart_interface': 'UART',
                'spi_interface': 'SPI',
                'i2c_interface': 'I2C',
                'timer_interface': '定时器',
                'adc_interface': 'ADC',
                'dac_interface': 'DAC',
                'pwm_interface': 'PWM',
                'can_interface': 'CAN',
                'usb_interface': 'USB',
                'ethernet_interface': '以太网',
                'dma_interface': 'DMA',

                # Mermaid Generation
                'no_call_relationships_found': '未找到调用关系',
                'no_main_function_or_call_relationships': '未找到main函数或调用关系',
                'adaptive_layout_description': '自适应布局说明:',
                'ui_width': 'UI宽度: {}px，每行节点数: {}',
                'red_main_function': '🔴 红色: main函数 (程序入口)',
                'green_hal_functions': '🟢 绿色: HAL/接口函数',
                'blue_user_functions': '🔵 蓝色: 用户定义函数',
                'hierarchical_flowchart_description': '层次化流程图说明:',
                'yellow_green_second_layer': '🟡 黄绿色: 第二层用户函数',
                'yellow_deeper_functions': '🟡 黄色: 更深层函数',
                'interface_usage_statistics_comment': '接口使用统计',
                'times_called': '次调用',

                # File scanning and analysis
                'skip_directories': '跳过目录',
                'analyzing_file': '分析文件: {}',
                'found_functions': '找到函数: {}',
                'found_includes': '找到包含文件: {}',
                'main_function_found': '找到main函数',
                'main_function_not_found': '未找到main函数',
                'includes_count': '包含文件: {} 个',
                'parsing_function_definitions_and_calls': '解析函数定义和调用...',
                'building_call_tree': '构建调用树...',
                'call_tree_construction_completed': '调用树构建完成',
                'functions_in_call_tree': '调用树中函数数量: {}',
                'call_tree_depth': '调用树深度: {}',

                # Comments and descriptions
                'graph_rendering_related': '图形渲染相关',
                'safe_json_serialization': '安全的JSON序列化函数，处理set等不可序列化的类型',
                'config_file_path_hidden': '配置文件路径（exe所在目录的隐藏文件）',
                'add_canvas_rounded_rect': '添加Canvas圆角矩形方法',
                'load_last_config': '加载上次的配置',
                'analysis_results_ensure_defaults': '分析结果 - 确保所有属性都有默认值',
                'config_dialog_already_shown': 'ConfigDialog已经在__init__中显示，不需要调用show()',
                'find_pdf_document': '查找PDF文档文件',
                'get_resource_file_path': '获取资源文件路径',
                'get_absolute_path_resource': '获取资源文件的绝对路径',
                'if_packaged_exe_temp_dir': '如果是打包的exe文件，资源在临时目录中',
                'if_python_script_dir': '如果是Python脚本，资源在脚本目录',
                'try_get_pdf_from_package': '尝试从打包的资源中获取PDF',
                'if_not_in_package_try_other': '如果打包资源中没有，再尝试其他位置',
                'get_exe_directory': '获取exe文件所在目录',
                'search_path_list': '搜索路径列表',
                'exe_directory': 'exe文件所在目录',
                'current_working_dir': '当前工作目录',
                'parent_directory': '上级目录',
                'exe_parent_directory': 'exe目录的上级目录',
                'open_document_by_os': '根据操作系统打开文档',
                'if_no_document_show_help': '如果找不到文档文件，显示简化帮助',
                'quick_start_colon': '快速开始：',
                'select_mcu_project_dir': '选择MCU项目目录',
                'configure_analysis_opts': '配置分析选项',
                'click_start_analysis': '点击"开始分析"',
                'view_analysis_results': '查看分析结果',
                'supported_project_types_colon': '支持的项目类型：',
                'keil_uvision_projects_ext': 'Keil uVision项目 (.uvprojx, .uvproj)',
                'cmake_projects_ext': 'CMake项目 (CMakeLists.txt)',
                'makefile_projects_simple': 'Makefile项目',
                'general_cpp_projects_simple': '通用C/C++项目',
                'llm_configuration_colon': 'LLM配置：',
                'supports_ollama_local_models': '支持Ollama本地模型',
                'supports_tencent_cloud_api': '支持腾讯云API',
                'config_llm_config_path': 'Config → LLM Config 进行配置',
                'complete_documentation_pdf': '完整文档：MCU_Code_Analyzer_Complete_Documentation.pdf',
                'fallback_to_simple_help': '降级到简化帮助',
                'quick_start_simple_flow': '快速开始：选择项目目录 → 配置选项 → 开始分析',
                'supported_formats_list': '支持格式：Keil/CMake/Makefile/通用C++项目',
                'llm_config_path_simple': 'LLM配置：Config → LLM Config',

                # Analysis process details
                'skip_some_directories': '跳过一些目录',
                'limit_analysis_file_count': '限制分析文件数量',
                'find_functions': '查找函数',
                'find_include_files': '查找包含文件',
                'change_to_list_not_set': '改为list而不是set',
                'get_call_depth_from_config': '从配置文件获取调用深度',
                'store_all_function_definitions_calls': '存储所有函数的定义和调用',
                'first_step': '第一步',
                'parse_all_function_definitions': '解析所有函数定义',
                'remove_comments_string_literals': '移除注释和字符串字面量',
                'avoid_misidentification': '避免误识别',
                'find_function_definitions': '查找函数定义',
                'second_step': '第二步',
                'analyze_function_call_relationships': '分析每个函数的调用关系',
                'analyze_internal_function_calls': '分析每个函数内部的调用关系',
                'build_call_tree_from_main': '从main函数开始构建调用树',
                'third_step': '第三步',
                'analyze_interface_usage': '分析接口使用',
                'only_count_functions_in_call_tree': '只统计调用树中的函数',
                'save_to_instance_for_mermaid': '保存到实例变量供Mermaid使用',
                'save_interface_info_for_llm': '保存接口使用信息供LLM使用',

                # Code processing and analysis
                'remove_c_comments_strings': '移除C代码中的注释和字符串字面量',
                'simplified_version': '简化版本',
                'remove_single_line_comments': '移除单行注释',
                'remove_multi_line_comments': '移除多行注释',
                'remove_string_literals': '移除字符串字面量',
                'extract_function_definitions': '提取函数定义',
                'regex_for_function_definitions': '匹配函数定义的正则表达式',
                'exclude_some_keywords': '排除一些关键字',
                'extract_function_calls': '提取函数调用',
                'regex_for_function_calls': '匹配函数调用的正则表达式',
                'exclude_keywords_non_function_calls': '排除一些关键字和常见的非函数调用',
                'find_all_function_positions_content': '找到文件中所有函数的定义位置和内容',
                'find_function_body_start': '找到函数体的开始位置',
                'function_body_start': '函数体开始的',
                'find_matching_closing_brace': '找到匹配的结束大括号',
                'find_function_calls_in_body': '在函数体中查找函数调用',
                'keep_only_defined_function_calls': '只保留在all_functions中定义的函数调用',
                'avoid_self_calls': '避免自调用',
                'update_function_call_list': '更新函数的调用列表',
                'remove_duplicates': '去重',
                'extract_function_body_content': '提取函数体内容',
                'from_start_brace_to_matching_end': '从开始大括号到匹配的结束大括号',
                'no_matching_closing_brace_found': '未找到匹配的结束大括号',

                # Call tree construction
                'build_call_tree': '构建调用树',
                'recursively_build_child_nodes': '递归构建子节点',
                'count_functions_in_call_tree': '统计调用树中的函数数量',
                'get_max_call_tree_depth': '获取调用树的最大深度',
                'analyze_interface_usage_in_call_tree': '分析调用树中的接口使用情况',
                'collect_all_function_names_in_call_tree': '收集调用树中的所有函数名',
                'interface_patterns': '接口模式',
                'search_interface_usage_in_call_tree_files': '只在调用树相关的文件中搜索接口使用',
                'check_if_file_contains_call_tree_functions': '检查文件中是否包含调用树中的函数',
                'only_count_function_calls': '只统计函数调用',
                'dont_count_definitions_comments': '不统计定义和注释',
                'only_return_used_interfaces': '只返回有使用的接口',
                'collect_all_function_names_from_call_tree': '从调用树中收集所有函数名',
                'interface_keyword_patterns': '接口关键字模式',
                'keep_only_used_interfaces': '只保留使用的接口',

                # Function call relationship analysis
                'extract_plain_text_function_call_relationships': '提取纯文本的函数调用关系',
                'no_call_relationship_analysis_performed': '未进行调用关系分析',
                'no_main_function_call_relationships_found': '未找到main函数调用关系',
                'recursively_extract_call_tree_text': '递归提取调用树的文本表示',
                'unknown_function': '未知函数',
                'main_function_program_entry': 'main函数 (程序入口)',
                'recursively_process_child_nodes': '递归处理子节点',
                'format_interface_info_for_prompt_clean': '格式化接口信息用于提示（无特殊字符）',
                'no_interface_usage_detected_clean': '未检测到接口使用',
                'times_called_clean': '次调用',
                'safe_get_chip_info': '安全获取芯片信息',
                'mcu_project_analysis_request': 'MCU项目分析请求',
                'project_overview': '项目概述',
                'project_path': '项目路径',
                'chip_model': '芯片型号',
                'chip_vendor': '芯片厂商',
                'processor_core': '处理器内核',
                'code_structure': '代码结构',
                'total_function_count': '总函数数量',
                'main_function_status': 'main函数',
                'exists': '存在',
                'not_found': '未找到',
                'include_file_count': '包含文件数',
                'interface_usage': '接口使用',
                'function_call_relationships': '函数调用关系',
                'analyze_based_on_above_info': '请基于以上信息分析，生成这个项目试用芯片信息和实现了什么具体功能，以及用到了芯片那些模块。',

                # User prompt template
                'mcu_project_analysis_request_title': 'MCU项目分析请求',
                'project_overview_title': '项目概述:',
                'project_path_label': '项目路径',
                'chip_model_label': '芯片型号',
                'chip_vendor_label': '芯片厂商',
                'processor_core_label': '处理器内核',
                'code_structure_title': '代码结构:',
                'total_function_count_label': '总函数数量',
                'main_function_label': 'main函数',
                'exists_label': '存在',
                'not_found_label': '未找到',
                'include_file_count_label': '包含文件数',
                'interface_usage_title': '接口使用:',
                'function_call_relationships_title': '函数调用关系:',
                'analyze_request_text': '请基于以上信息分析，生成这个项目试用芯片信息和实现了什么具体功能，以及用到了芯片那些模块。',

                # LLM Configuration Dialog
                'llm_config': 'LLM配置',
                'llm_service_config': 'LLM服务配置',
                'select_llm_service': '选择LLM服务',
                'ollama_local': 'Ollama (本地)',
                'tencent_cloud': '腾讯云',
                'config_parameters': '配置参数',
                'service_address': '服务地址:',
                'model_name': '模型名称:',
                'api_id': 'API ID:',
                'api_key': 'API密钥:',
                'config_description': '配置说明:',
                'ollama_description': 'Ollama: 本地免费服务，只需服务地址和模型名称',
                'tencent_description': '腾讯云: 需要API ID和API密钥',
                'test_connection': '测试连接',
                'save': '保存',
                'cancel': '取消',
                'llm_config_saved': 'LLM配置已保存！\\n注意：当前为简化配置模式',
                'connection_test_in_development': '连接测试功能正在开发中...',

                # Analysis Configuration Dialog
                'analysis_config': '分析配置',
                'analysis_options': '分析选项',
                'deep_code_analysis': '深度代码分析',
                'main_function_call_analysis': 'main函数调用分析',
                'generate_analysis_report': '生成分析报告',
                'show_call_flowchart': '显示调用流程图',
                'call_depth_settings': '调用深度设置',
                'call_depth': '调用深度:',
                'call_depth_description': '设置函数调用关系分析的最大深度\\n深度越大，分析越详细，但耗时更长',
                'reset_defaults': '重置默认',
                'config_saved_successfully': '配置已保存成功！',
                'save_config_failed': '保存配置失败',
            }
        }
    
    def get_text(self, key, *args):
        """Get localized text"""
        text = self.texts.get(self.language, self.texts['en']).get(key, key)
        if args:
            return text.format(*args)
        return text
    
    def set_language(self, language):
        """Set current language"""
        if language in self.texts:
            self.language = language
    
    def get_available_languages(self):
        """Get available languages"""
        return list(self.texts.keys())

# Global localization instance
loc = Localization()  # Load language from config file
