"""
LLM管理器 - 支持多种LLM服务的统一接口
"""

import json
import requests
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
import subprocess
import time
import hashlib
import hmac
import base64
from datetime import datetime
from dataclasses import dataclass
from utils.logger import logger, log_decorator, performance_monitor
from utils.config import config, LLMConfig


@dataclass
class LLMResponse:
    """LLM响应数据类"""
    content: str
    success: bool
    error_message: str = ""
    usage: Dict[str, int] = None
    model: str = ""
    provider: str = ""
    response_time: float = 0.0


class LLMClient(ABC):
    """LLM客户端抽象基类"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """设置会话"""
        if self.config.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            })
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """生成文本"""
        pass
    
    @abstractmethod
    async def generate_async(self, prompt: str, **kwargs) -> LLMResponse:
        """异步生成文本"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查服务是否可用"""
        pass


class OpenAIClient(LLMClient):
    """OpenAI兼容API客户端"""
    
    @log_decorator
    @performance_monitor
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """同步生成"""
        start_time = time.time()
        
        try:
            # 构建请求数据
            request_data = {
                "model": self.config.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens)
            }
            
            # 发送请求
            response = self.session.post(
                f"{self.config.base_url}/chat/completions",
                json=request_data,
                timeout=kwargs.get("timeout", self.config.timeout)
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                usage = result.get("usage", {})
                
                logger.info(f"OpenAI API调用成功 (耗时: {response_time:.2f}s)")
                return LLMResponse(
                    content=content,
                    success=True,
                    usage=usage,
                    model=self.config.model,
                    provider="openai",
                    response_time=response_time
                )
            else:
                error_msg = f"API错误: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return LLMResponse(
                    content="",
                    success=False,
                    error_message=error_msg,
                    provider="openai",
                    response_time=response_time
                )
                
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"OpenAI API调用失败: {e}"
            logger.error(error_msg)
            return LLMResponse(
                content="",
                success=False,
                error_message=error_msg,
                provider="openai",
                response_time=response_time
            )
    
    async def generate_async(self, prompt: str, **kwargs) -> LLMResponse:
        """异步生成"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.generate, prompt, **kwargs)
    
    def is_available(self) -> bool:
        """检查OpenAI API是否可用"""
        try:
            response = self.session.get(
                f"{self.config.base_url}/models",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False


class OllamaClient(LLMClient):
    """Ollama本地LLM客户端"""
    
    @log_decorator
    @performance_monitor
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """同步生成"""
        start_time = time.time()
        
        try:
            request_data = {
                "model": self.config.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", self.config.temperature),
                    "top_p": kwargs.get("top_p", 0.9),
                    "num_predict": kwargs.get("max_tokens", self.config.max_tokens)
                }
            }
            
            response = self.session.post(
                f"{self.config.base_url}/api/generate",
                json=request_data,
                timeout=kwargs.get("timeout", self.config.timeout)
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("response", "")
                
                logger.info(f"Ollama调用成功 (耗时: {response_time:.2f}s)")
                return LLMResponse(
                    content=content,
                    success=True,
                    model=self.config.model,
                    provider="ollama",
                    response_time=response_time
                )
            else:
                error_msg = f"Ollama错误: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return LLMResponse(
                    content="",
                    success=False,
                    error_message=error_msg,
                    provider="ollama",
                    response_time=response_time
                )
                
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"Ollama调用失败: {e}"
            logger.error(error_msg)
            return LLMResponse(
                content="",
                success=False,
                error_message=error_msg,
                provider="ollama",
                response_time=response_time
            )
    
    async def generate_async(self, prompt: str, **kwargs) -> LLMResponse:
        """异步生成"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.generate, prompt, **kwargs)
    
    def is_available(self) -> bool:
        """检查Ollama是否可用"""
        try:
            logger.info(f"Testing Ollama connection to: {self.config.base_url}/api/tags")
            response = self.session.get(f"{self.config.base_url}/api/tags", timeout=5)
            logger.info(f"Ollama response status: {response.status_code}")
            if response.status_code == 200:
                logger.info("✅ Ollama connection successful")
                return True
            else:
                logger.warning(f"❌ Ollama connection failed with status: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Ollama connection error: {e}")
            return False
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        try:
            response = self.session.get(f"{self.config.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
        except Exception as e:
            logger.error(f"获取Ollama模型列表失败: {e}")
        return []


class LocalCommandClient(LLMClient):
    """本地命令行LLM客户端"""
    
    def __init__(self, config: LLMConfig, command_template: str = None):
        super().__init__(config)
        self.command_template = command_template or "ollama run {model} '{prompt}'"
    
    @log_decorator
    @performance_monitor
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """通过命令行调用本地LLM"""
        start_time = time.time()
        
        try:
            # 清理提示词中的特殊字符
            clean_prompt = prompt.replace("'", "\\'").replace('"', '\\"')
            
            command = self.command_template.format(
                model=self.config.model,
                prompt=clean_prompt
            )
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=kwargs.get("timeout", self.config.timeout)
            )
            
            response_time = time.time() - start_time
            
            if result.returncode == 0:
                content = result.stdout.strip()
                logger.info(f"本地命令调用成功 (耗时: {response_time:.2f}s)")
                return LLMResponse(
                    content=content,
                    success=True,
                    model=self.config.model,
                    provider="local_command",
                    response_time=response_time
                )
            else:
                error_msg = f"命令执行失败: {result.stderr}"
                logger.error(error_msg)
                return LLMResponse(
                    content="",
                    success=False,
                    error_message=error_msg,
                    provider="local_command",
                    response_time=response_time
                )
                
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"本地命令调用失败: {e}"
            logger.error(error_msg)
            return LLMResponse(
                content="",
                success=False,
                error_message=error_msg,
                provider="local_command",
                response_time=response_time
            )
    
    async def generate_async(self, prompt: str, **kwargs) -> LLMResponse:
        """异步生成"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.generate, prompt, **kwargs)
    
    def is_available(self) -> bool:
        """检查本地命令是否可用"""
        try:
            # 尝试执行一个简单的命令来检查可用性
            test_command = self.command_template.format(
                model=self.config.model,
                prompt="test"
            )
            result = subprocess.run(
                test_command,
                shell=True,
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False


class TencentClient(LLMClient):
    """腾讯云LLM客户端"""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.secret_id = config.api_key.split(':')[0] if ':' in config.api_key else config.api_key
        self.secret_key = config.api_key.split(':')[1] if ':' in config.api_key else ""
        self.region = getattr(config, 'region', 'ap-beijing')

    def _generate_signature(self, method: str, uri: str, query: str, headers: dict, payload: str) -> str:
        """生成腾讯云API签名"""
        # 构建规范请求串
        canonical_headers = ""
        signed_headers = ""

        # 对headers按key排序
        sorted_headers = sorted(headers.items())
        for key, value in sorted_headers:
            canonical_headers += f"{key.lower()}:{value}\n"
            signed_headers += f"{key.lower()};"

        signed_headers = signed_headers[:-1]  # 移除最后的分号

        canonical_request = f"{method}\n{uri}\n{query}\n{canonical_headers}\n{signed_headers}\n{hashlib.sha256(payload.encode('utf-8')).hexdigest()}"

        # 构建待签名字符串
        algorithm = "TC3-HMAC-SHA256"
        timestamp = str(int(time.time()))
        date = datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d')
        credential_scope = f"{date}/hunyuan/tc3_request"
        string_to_sign = f"{algorithm}\n{timestamp}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"

        # 计算签名
        secret_date = hmac.new(f"TC3{self.secret_key}".encode('utf-8'), date.encode('utf-8'), hashlib.sha256).digest()
        secret_service = hmac.new(secret_date, "hunyuan".encode('utf-8'), hashlib.sha256).digest()
        secret_signing = hmac.new(secret_service, "tc3_request".encode('utf-8'), hashlib.sha256).digest()
        signature = hmac.new(secret_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

        return signature, timestamp, signed_headers

    @log_decorator
    @performance_monitor
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """同步生成"""
        start_time = time.time()

        try:
            # 构建请求数据
            request_data = {
                "Model": self.config.model or "hunyuan-lite",
                "Messages": [{"Role": "user", "Content": prompt}],
                "Temperature": kwargs.get("temperature", self.config.temperature),
                "TopP": kwargs.get("top_p", 0.8),
                "Stream": False
            }

            payload = json.dumps(request_data)

            # 构建请求头
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "Host": "hunyuan.tencentcloudapi.com",
                "X-TC-Action": "ChatCompletions",
                "X-TC-Version": "2023-09-01",
                "X-TC-Region": self.region
            }

            # 生成签名
            signature, timestamp, signed_headers = self._generate_signature(
                "POST", "/", "", headers, payload
            )

            # 添加授权头
            authorization = f"TC3-HMAC-SHA256 Credential={self.secret_id}/{datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d')}/hunyuan/tc3_request, SignedHeaders={signed_headers}, Signature={signature}"
            headers["Authorization"] = authorization
            headers["X-TC-Timestamp"] = timestamp

            # 发送请求
            response = self.session.post(
                "https://hunyuan.tencentcloudapi.com/",
                headers=headers,
                data=payload,
                timeout=kwargs.get("timeout", self.config.timeout)
            )

            response_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()

                if "Error" in result["Response"]:
                    error_msg = f"腾讯API错误: {result['Response']['Error']['Message']}"
                    logger.error(error_msg)
                    return LLMResponse(
                        content="",
                        success=False,
                        error_message=error_msg,
                        provider="tencent",
                        response_time=response_time
                    )

                choices = result["Response"].get("Choices", [])
                if choices:
                    content = choices[0]["Message"]["Content"]
                    usage = result["Response"].get("Usage", {})

                    logger.info(f"腾讯API调用成功 (耗时: {response_time:.2f}s)")
                    return LLMResponse(
                        content=content,
                        success=True,
                        usage=usage,
                        model=self.config.model,
                        provider="tencent",
                        response_time=response_time
                    )
                else:
                    error_msg = "腾讯API返回空响应"
                    logger.error(error_msg)
                    return LLMResponse(
                        content="",
                        success=False,
                        error_message=error_msg,
                        provider="tencent",
                        response_time=response_time
                    )
            else:
                error_msg = f"腾讯API错误: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return LLMResponse(
                    content="",
                    success=False,
                    error_message=error_msg,
                    provider="tencent",
                    response_time=response_time
                )

        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"腾讯API调用失败: {e}"
            logger.error(error_msg)
            return LLMResponse(
                content="",
                success=False,
                error_message=error_msg,
                provider="tencent",
                response_time=response_time
            )

    async def generate_async(self, prompt: str, **kwargs) -> LLMResponse:
        """异步生成"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.generate, prompt, **kwargs)

    def is_available(self) -> bool:
        """检查腾讯API是否可用"""
        if not self.secret_id or not self.secret_key:
            return False

        try:
            # 发送一个简单的测试请求
            test_response = self.generate("test", timeout=10)
            return test_response.success or "认证" not in test_response.error_message.lower()
        except:
            return False


class LLMManager:
    """LLM管理器 - 统一管理多个LLM客户端"""
    
    def __init__(self):
        self.clients: Dict[str, LLMClient] = {}
        self.current_provider = None
        self.fallback_order = ['ollama', 'openai', 'tencent', 'custom']
        self._initialize_clients()
    
    def _initialize_clients(self):
        """初始化LLM客户端"""
        logger.info("初始化LLM客户端...")
        
        # 初始化Ollama客户端
        ollama_config = config.get_llm_config('ollama')
        if ollama_config:
            ollama_client = OllamaClient(ollama_config)
            self.clients['ollama'] = ollama_client
            if ollama_client.is_available():
                logger.info("✅ Ollama客户端可用")
                if not self.current_provider:
                    self.current_provider = 'ollama'
            else:
                logger.warning("⚠️ Ollama客户端不可用")
        
        # 初始化OpenAI客户端
        openai_config = config.get_llm_config('openai')
        if openai_config and openai_config.api_key:
            openai_client = OpenAIClient(openai_config)
            self.clients['openai'] = openai_client
            if openai_client.is_available():
                logger.info("✅ OpenAI客户端可用")
                if not self.current_provider:
                    self.current_provider = 'openai'
            else:
                logger.warning("⚠️ OpenAI客户端不可用")
        
        # 初始化腾讯客户端
        tencent_config = config.get_llm_config('tencent')
        if tencent_config and tencent_config.api_key:
            tencent_client = TencentClient(tencent_config)
            self.clients['tencent'] = tencent_client
            if tencent_client.is_available():
                logger.info("✅ 腾讯云API客户端可用")
                if not self.current_provider:
                    self.current_provider = 'tencent'
            else:
                logger.warning("⚠️ 腾讯云API客户端不可用")

        # 初始化自定义客户端
        custom_config = config.get_llm_config('custom')
        if custom_config and custom_config.base_url:
            custom_client = OpenAIClient(custom_config)  # 使用OpenAI兼容格式
            self.clients['custom'] = custom_client
            if custom_client.is_available():
                logger.info("✅ 自定义API客户端可用")
                if not self.current_provider:
                    self.current_provider = 'custom'
            else:
                logger.warning("⚠️ 自定义API客户端不可用")
        
        if self.current_provider:
            logger.info(f"🎯 当前使用: {self.current_provider}")
        else:
            logger.warning("❌ 没有可用的LLM客户端")
    
    @log_decorator
    def generate(self, prompt: str, provider: str = None, **kwargs) -> LLMResponse:
        """生成文本 - 支持自动重试和降级"""
        if provider and provider in self.clients:
            # 使用指定的提供商
            return self.clients[provider].generate(prompt, **kwargs)
        
        # 使用当前提供商或按优先级尝试
        providers_to_try = [self.current_provider] if self.current_provider else []
        providers_to_try.extend([p for p in self.fallback_order if p not in providers_to_try])
        
        for provider_name in providers_to_try:
            if provider_name in self.clients:
                logger.info(f"尝试使用 {provider_name}")
                response = self.clients[provider_name].generate(prompt, **kwargs)
                
                if response.success:
                    self.current_provider = provider_name
                    return response
                else:
                    logger.warning(f"{provider_name} 调用失败: {response.error_message}")
        
        # All clients failed
        logger.error("All LLM clients failed")
        return LLMResponse(
            content="",
            success=False,
            error_message="All LLM clients unavailable",
            provider="none"
        )

    async def generate_async(self, prompt: str, provider: str = None, **kwargs) -> LLMResponse:
        """异步生成文本"""
        if provider and provider in self.clients:
            return await self.clients[provider].generate_async(prompt, **kwargs)

        providers_to_try = [self.current_provider] if self.current_provider else []
        providers_to_try.extend([p for p in self.fallback_order if p not in providers_to_try])

        for provider_name in providers_to_try:
            if provider_name in self.clients:
                response = await self.clients[provider_name].generate_async(prompt, **kwargs)
                if response.success:
                    self.current_provider = provider_name
                    return response

        return LLMResponse(
            content="",
            success=False,
            error_message="All LLM clients unavailable",
            provider="none"
        )

    def is_available(self) -> bool:
        """检查是否有可用的LLM服务"""
        return len(self.get_available_providers()) > 0

    def get_available_providers(self) -> List[str]:
        """获取可用的提供商列表"""
        available = []
        for provider, client in self.clients.items():
            if client.is_available():
                available.append(provider)
        return available

    def get_provider_info(self) -> Dict[str, Dict[str, any]]:
        """获取提供商信息"""
        info = {}
        for provider, client in self.clients.items():
            info[provider] = {
                'available': client.is_available(),
                'model': client.config.model,
                'base_url': client.config.base_url,
                'provider_type': type(client).__name__
            }
        return info

    def set_current_provider(self, provider: str) -> bool:
        """设置当前提供商"""
        if provider in self.clients and self.clients[provider].is_available():
            self.current_provider = provider
            logger.info(f"切换到提供商: {provider}")
            return True
        else:
            logger.error(f"提供商不可用: {provider}")
            return False

    def add_client(self, name: str, client: LLMClient):
        """添加新的LLM客户端"""
        self.clients[name] = client
        if client.is_available() and not self.current_provider:
            self.current_provider = name
        logger.info(f"添加LLM客户端: {name}")

    def remove_client(self, name: str):
        """移除LLM客户端"""
        if name in self.clients:
            del self.clients[name]
            if self.current_provider == name:
                # 重新选择可用的提供商
                available = self.get_available_providers()
                self.current_provider = available[0] if available else None
            logger.info(f"移除LLM客户端: {name}")

    def test_connection(self, provider: str = None) -> Dict[str, any]:
        """测试连接"""
        if provider:
            providers_to_test = [provider] if provider in self.clients else []
        else:
            providers_to_test = list(self.clients.keys())

        results = {}
        for provider_name in providers_to_test:
            client = self.clients[provider_name]
            start_time = time.time()

            try:
                available = client.is_available()
                response_time = time.time() - start_time

                results[provider_name] = {
                    'available': available,
                    'response_time': response_time,
                    'model': client.config.model,
                    'error': None
                }

                if available:
                    logger.info(f"✅ {provider_name} 连接正常 ({response_time:.2f}s)")
                else:
                    logger.warning(f"❌ {provider_name} 连接失败")

            except Exception as e:
                response_time = time.time() - start_time
                results[provider_name] = {
                    'available': False,
                    'response_time': response_time,
                    'model': client.config.model,
                    'error': str(e)
                }
                logger.error(f"❌ {provider_name} 测试失败: {e}")

        return results

    def test_connection_with_config(self, provider: str, test_config: LLMConfig) -> Dict[str, any]:
        """使用指定配置测试连接"""
        import time

        start_time = time.time()

        try:
            # 创建临时客户端进行测试
            if provider == 'ollama':
                test_client = OllamaClient(test_config)
            elif provider == 'tencent_api':
                test_client = TencentClient(test_config)
            elif provider in ['openai', 'custom']:
                test_client = OpenAIClient(test_config)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported provider: {provider}',
                    'response_time': 0
                }

            # 测试连接
            available = test_client.is_available()
            response_time = int((time.time() - start_time) * 1000)  # 转换为毫秒

            if available:
                # 尝试发送一个简单的测试请求
                try:
                    test_response = test_client.generate("Hello", max_tokens=5, timeout=10)
                    if test_response and test_response.success:
                        return {
                            'success': True,
                            'response_time': response_time,
                            'provider': provider,
                            'model': test_config.model,
                            'response_content': test_response.content[:50] + "..." if len(test_response.content) > 50 else test_response.content
                        }
                    else:
                        error_detail = test_response.error_message if test_response else "No response object"
                        return {
                            'success': False,
                            'error': f'Test request failed: {error_detail}',
                            'response_time': response_time
                        }
                except Exception as e:
                    return {
                        'success': False,
                        'error': f'Test request exception: {str(e)}',
                        'response_time': response_time
                    }
            else:
                return {
                    'success': False,
                    'error': 'Service not available',
                    'response_time': response_time
                }

        except Exception as e:
            response_time = int((time.time() - start_time) * 1000)
            return {
                'success': False,
                'error': str(e),
                'response_time': response_time
            }

    def get_models(self, provider: str = None) -> Dict[str, List[str]]:
        """获取可用模型列表"""
        models = {}

        providers_to_check = [provider] if provider else self.clients.keys()

        for provider_name in providers_to_check:
            if provider_name in self.clients:
                client = self.clients[provider_name]
                if hasattr(client, 'get_available_models'):
                    try:
                        models[provider_name] = client.get_available_models()
                    except Exception as e:
                        logger.error(f"获取{provider_name}模型列表失败: {e}")
                        models[provider_name] = []
                else:
                    models[provider_name] = [client.config.model]

        return models

    def update_config(self, provider: str, new_config: LLMConfig):
        """更新提供商配置"""
        if provider in self.clients:
            # 创建新的客户端实例
            if provider == 'ollama':
                new_client = OllamaClient(new_config)
            elif provider in ['openai', 'custom']:
                new_client = OpenAIClient(new_config)
            elif provider == 'tencent':
                new_client = TencentClient(new_config)
            else:
                logger.error(f"不支持的提供商类型: {provider}")
                return False

            # 替换客户端
            self.clients[provider] = new_client
            config.update_llm_config(provider, new_config)

            logger.info(f"更新{provider}配置成功")
            return True
        else:
            logger.error(f"提供商不存在: {provider}")
            return False


# 全局LLM管理器实例
llm_manager = LLMManager()
