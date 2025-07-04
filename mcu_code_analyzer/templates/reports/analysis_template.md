# STM32工程分析报告

**项目名称**: {{project_name}}  
**分析时间**: {{analysis_time}}  
**分析工具**: STM32工程分析器 v2.0  
**项目路径**: {{project_path}}

---

## 📋 执行摘要

{{executive_summary}}

### 关键发现
{{#key_findings}}
- {{.}}
{{/key_findings}}

### 建议优先级
{{#recommendations}}
- **{{priority}}**: {{description}}
{{/recommendations}}

---

## 🔧 项目概览

### 基本信息
| 项目属性 | 值 |
|---------|-----|
| 项目名称 | {{project_info.name}} |
| 项目类型 | {{project_info.type}} |
| 编译器 | {{project_info.compiler}} |
| 源文件数量 | {{project_info.source_files_count}} |
| 头文件数量 | {{project_info.header_files_count}} |
| 包含路径数量 | {{project_info.include_paths_count}} |

### 项目结构
```
{{project_structure}}
```

---

## 💻 芯片信息

### 硬件平台
| 芯片属性 | 值 |
|---------|-----|
| 设备型号 | {{chip_info.device_name}} |
| 厂商 | {{chip_info.vendor}} |
| 系列 | {{chip_info.series}} |
| CPU内核 | {{chip_info.core}} |
| Flash大小 | {{chip_info.flash_size}} |
| RAM大小 | {{chip_info.ram_size}} |
| 主频 | {{chip_info.frequency}} |
| 封装 | {{chip_info.package}} |

### 芯片特性
{{#chip_features}}
- {{.}}
{{/chip_features}}

### 适用场景
{{chip_applications}}

---

## 📊 代码分析

### 函数统计
| 统计项 | 数量 | 占比 |
|--------|------|------|
| 总函数数量 | {{function_stats.total_functions}} | 100% |
| 已定义函数 | {{function_stats.defined_functions}} | {{function_stats.defined_percentage}}% |
| 声明函数 | {{function_stats.declared_functions}} | {{function_stats.declared_percentage}}% |
| 静态函数 | {{function_stats.static_functions}} | {{function_stats.static_percentage}}% |
| 内联函数 | {{function_stats.inline_functions}} | {{function_stats.inline_percentage}}% |
| main可达函数 | {{function_stats.main_reachable}} | {{function_stats.reachable_percentage}}% |

### 调用关系分析
- **总调用次数**: {{call_stats.total_calls}}
- **调用者数量**: {{call_stats.unique_callers}}
- **被调用者数量**: {{call_stats.unique_callees}}
- **平均调用深度**: {{call_stats.average_depth}}

### 主要函数调用链
```
{{main_call_chain}}
```

### 代码复杂度评估
| 复杂度指标 | 值 | 评级 |
|-----------|-----|------|
| 圈复杂度 | {{complexity.cyclomatic}} | {{complexity.cyclomatic_grade}} |
| 函数长度 | {{complexity.function_length}} | {{complexity.length_grade}} |
| 嵌套深度 | {{complexity.nesting_depth}} | {{complexity.nesting_grade}} |
| 耦合度 | {{complexity.coupling}} | {{complexity.coupling_grade}} |

---

## 🔌 接口分析

### 接口使用统计
检测到 **{{interface_summary.total_enabled}}** 个启用的接口：

{{#interface_details}}
#### {{name}} - {{description}}
- **厂商**: {{vendor}}
- **函数数量**: {{function_count}}
- **调用次数**: {{call_count}}
- **主要函数**: {{main_functions}}

{{/interface_details}}

### 厂商分布
{{#vendor_distribution}}
- **{{vendor}}**: {{count}} 个接口
{{/vendor_distribution}}

### 接口使用热力图
```
{{interface_heatmap}}
```

---

## 🤖 智能分析

### 项目总结
{{ai_analysis.project_overview}}

### 主要功能
{{ai_analysis.main_functionality}}

### 业务逻辑识别
{{#business_logics}}
#### {{name}}
{{description}}

**相关函数**: {{functions}}
{{/business_logics}}

### 架构模式检测
{{#architectural_patterns}}
#### {{pattern_type}} (置信度: {{confidence}})
{{description}}

**证据**:
{{#evidence}}
- {{.}}
{{/evidence}}
{{/architectural_patterns}}

---

## 📈 质量评估

### 可维护性评分
**总分**: {{quality.maintainability_score}}/100

### 质量指标
| 指标 | 评分 | 说明 |
|------|------|------|
| 代码结构 | {{quality.structure_score}}/100 | {{quality.structure_comment}} |
| 命名规范 | {{quality.naming_score}}/100 | {{quality.naming_comment}} |
| 错误处理 | {{quality.error_handling_score}}/100 | {{quality.error_handling_comment}} |
| 文档完整性 | {{quality.documentation_score}}/100 | {{quality.documentation_comment}} |

### 性能瓶颈
{{#performance_bottlenecks}}
- **{{type}}**: {{description}}
  - 影响: {{impact}}
  - 建议: {{suggestion}}
{{/performance_bottlenecks}}

### 安全性分析
{{#security_concerns}}
- **{{level}}**: {{description}}
  - 风险: {{risk}}
  - 缓解措施: {{mitigation}}
{{/security_concerns}}

---

## 🔄 移植建议

### STM32到NXP转换评估
- **可行性**: {{conversion.feasibility}}
- **复杂度**: {{conversion.complexity}}
- **预估工作量**: {{conversion.effort}}

### 主要转换点
{{#conversion_points}}
#### {{category}}
- **STM32**: {{stm32_approach}}
- **NXP**: {{nxp_approach}}
- **转换难度**: {{difficulty}}
- **注意事项**: {{notes}}
{{/conversion_points}}

### 接口映射表
| STM32接口 | NXP对应接口 | 兼容性 | 备注 |
|-----------|-------------|--------|------|
{{#interface_mappings}}
| {{stm32_interface}} | {{nxp_interface}} | {{compatibility}} | {{notes}} |
{{/interface_mappings}}

---

## 📋 优化建议

### 代码优化
{{#code_optimizations}}
#### {{category}}
**优先级**: {{priority}}

**问题描述**: {{problem}}

**建议方案**: {{solution}}

**预期收益**: {{benefit}}
{{/code_optimizations}}

### 架构优化
{{#architecture_optimizations}}
- **{{aspect}}**: {{recommendation}}
{{/architecture_optimizations}}

### 性能优化
{{#performance_optimizations}}
- **{{area}}**: {{suggestion}}
  - 预期提升: {{improvement}}
  - 实施难度: {{difficulty}}
{{/performance_optimizations}}

---

## 📚 技术债务

### 识别的技术债务
{{#technical_debt}}
#### {{category}} - {{severity}}
**描述**: {{description}}

**影响**: {{impact}}

**解决方案**: {{solution}}

**预估工作量**: {{effort}}
{{/technical_debt}}

### 重构建议
{{#refactoring_suggestions}}
- **{{module}}**: {{suggestion}}
{{/refactoring_suggestions}}

---

## 🎯 下一步行动

### 短期目标 (1-2周)
{{#short_term_goals}}
- [ ] {{.}}
{{/short_term_goals}}

### 中期目标 (1-2个月)
{{#medium_term_goals}}
- [ ] {{.}}
{{/medium_term_goals}}

### 长期目标 (3-6个月)
{{#long_term_goals}}
- [ ] {{.}}
{{/long_term_goals}}

---

## 📖 附录

### 分析方法说明
本报告使用STM32工程分析器v2.0生成，采用以下分析方法：
1. 静态代码分析
2. 语法树解析
3. 调用关系追踪
4. 接口模式匹配
5. LLM智能分析
6. 语义理解

### 工具配置
- **LLM提供商**: {{llm_config.provider}}
- **模型**: {{llm_config.model}}
- **分析深度**: {{analysis_config.depth}}
- **启用功能**: {{analysis_config.enabled_features}}

### 免责声明
本报告基于自动化分析生成，建议结合人工审查使用。分析结果仅供参考，具体实施请根据项目实际情况调整。

---

*报告生成时间: {{generation_time}}*  
*STM32工程分析器 v2.0 - 智能分析，精准洞察*
