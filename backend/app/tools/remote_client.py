"""
远程 GPU 服务器 SSH 客户端模块。

管理与云端 GPU 服务器的 SSH 连接，用于触发训练和推理脚本。
使用 Paramiko 实现异步 SSH 操作，支持命令执行和文件传输。
"""

import asyncio
from pathlib import Path
from typing import Optional
import paramiko
from paramiko import SSHClient, SFTPClient
from paramiko.ssh_exception import SSHException, AuthenticationException

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class RemoteClient:
    """
    远程服务器 SSH 客户端。
    
    提供异步接口用于：
    - 执行远程命令
    - 上传/下载文件（SFTP）
    - 管理 SSH 连接生命周期
    """
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        key_path: Optional[str] = None,
        password: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> None:
        """
        初始化远程客户端。
        
        Args:
            host: 远程服务器地址（默认从配置读取）
            port: SSH 端口（默认从配置读取）
            username: SSH 用户名（默认从配置读取）
            key_path: SSH 私钥路径（默认从配置读取）
            password: SSH 密码（默认从配置读取，优先级低于 key_path）
            timeout: 连接超时时间（秒，默认从配置读取）
        """
        self.host = host or settings.remote_host
        self.port = port or settings.remote_port
        self.username = username or settings.remote_user
        self.key_path = key_path or settings.remote_key_path
        self.password = password or settings.remote_password
        self.timeout = timeout or settings.remote_timeout
        
        self._ssh_client: Optional[SSHClient] = None
        self._sftp_client: Optional[SFTPClient] = None
        
        logger.info(
            f"RemoteClient 初始化: {self.username}@{self.host}:{self.port}"
        )
    
    async def connect(self) -> None:
        """
        建立 SSH 连接。
        
        在事件循环中运行同步的 Paramiko 操作。
        """
        if self._ssh_client is not None:
            logger.warning("SSH 连接已存在，跳过连接")
            return
        
        try:
            # 在线程池中运行同步 SSH 连接
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._connect_sync)
            logger.info(f"SSH 连接成功: {self.host}")
        except Exception as e:
            logger.error(f"SSH 连接失败: {e}", exc_info=True)
            raise
    
    def _connect_sync(self) -> None:
        """
        同步建立 SSH 连接（在线程池中运行）。
        """
        self._ssh_client = SSHClient()
        self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # 准备认证参数
        auth_kwargs = {
            "username": self.username,
            "timeout": self.timeout,
        }
        
        # 优先使用密钥认证
        if self.key_path and Path(self.key_path).exists():
            auth_kwargs["key_filename"] = self.key_path
            logger.info(f"使用密钥认证: {self.key_path}")
        elif self.password:
            auth_kwargs["password"] = self.password
            logger.info("使用密码认证")
        else:
            raise ValueError("必须提供 SSH 密钥路径或密码")
        
        # 建立连接
        self._ssh_client.connect(
            hostname=self.host,
            port=self.port,
            **auth_kwargs
        )
        
        # 创建 SFTP 客户端
        self._sftp_client = self._ssh_client.open_sftp()
    
    async def disconnect(self) -> None:
        """
        关闭 SSH 连接。
        """
        if self._sftp_client:
            try:
                self._sftp_client.close()
            except Exception as e:
                logger.warning(f"关闭 SFTP 连接时出错: {e}")
            self._sftp_client = None
        
        if self._ssh_client:
            try:
                self._ssh_client.close()
            except Exception as e:
                logger.warning(f"关闭 SSH 连接时出错: {e}")
            self._ssh_client = None
        
        logger.info("SSH 连接已关闭")
    
    async def execute_command(
        self,
        command: str,
        timeout: Optional[int] = None
    ) -> tuple[int, str, str]:
        """
        在远程服务器上执行命令。
        
        Args:
            command: 要执行的命令
            timeout: 命令超时时间（秒），None 表示使用默认值
            
        Returns:
            (退出码, 标准输出, 标准错误) 元组
        """
        if self._ssh_client is None:
            await self.connect()
        
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._execute_command_sync,
                command,
                timeout or self.timeout
            )
            
            exit_code, stdout, stderr = result
            logger.info(
                f"命令执行完成: {command[:50]}... "
                f"(退出码: {exit_code})"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"命令执行失败: {command[:50]}... - {e}", exc_info=True)
            raise
    
    def _execute_command_sync(
        self,
        command: str,
        timeout: int
    ) -> tuple[int, str, str]:
        """
        同步执行命令（在线程池中运行）。
        
        Args:
            command: 要执行的命令
            timeout: 命令超时时间（秒）
            
        Returns:
            (退出码, 标准输出, 标准错误) 元组
        """
        stdin, stdout, stderr = self._ssh_client.exec_command(
            command,
            timeout=timeout
        )
        
        # 等待命令完成并读取输出
        exit_code = stdout.channel.recv_exit_status()
        stdout_text = stdout.read().decode("utf-8", errors="ignore")
        stderr_text = stderr.read().decode("utf-8", errors="ignore")
        
        return exit_code, stdout_text, stderr_text
    
    async def upload_file(
        self,
        local_path: str,
        remote_path: str
    ) -> None:
        """
        上传文件到远程服务器。
        
        Args:
            local_path: 本地文件路径
            remote_path: 远程文件路径
        """
        if self._sftp_client is None:
            await self.connect()
        
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._upload_file_sync,
                local_path,
                remote_path
            )
            logger.info(f"文件上传成功: {local_path} -> {remote_path}")
            
        except Exception as e:
            logger.error(
                f"文件上传失败: {local_path} -> {remote_path} - {e}",
                exc_info=True
            )
            raise
    
    def _upload_file_sync(self, local_path: str, remote_path: str) -> None:
        """
        同步上传文件（在线程池中运行）。
        
        Args:
            local_path: 本地文件路径
            remote_path: 远程文件路径
        """
        # 确保远程目录存在
        remote_dir = str(Path(remote_path).parent)
        try:
            self._sftp_client.stat(remote_dir)
        except FileNotFoundError:
            # 目录不存在，创建它（包括父目录）
            parts = remote_dir.strip("/").split("/")
            current_path = ""
            for part in parts:
                current_path = f"{current_path}/{part}" if current_path else f"/{part}"
                try:
                    self._sftp_client.mkdir(current_path)
                except IOError:
                    # 目录可能已存在，忽略错误
                    pass
        
        # 上传文件
        self._sftp_client.put(local_path, remote_path)
    
    async def download_file(
        self,
        remote_path: str,
        local_path: str
    ) -> None:
        """
        从远程服务器下载文件。
        
        Args:
            remote_path: 远程文件路径
            local_path: 本地文件路径
        """
        if self._sftp_client is None:
            await self.connect()
        
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._download_file_sync,
                remote_path,
                local_path
            )
            logger.info(f"文件下载成功: {remote_path} -> {local_path}")
            
        except Exception as e:
            logger.error(
                f"文件下载失败: {remote_path} -> {local_path} - {e}",
                exc_info=True
            )
            raise
    
    def _download_file_sync(self, remote_path: str, local_path: str) -> None:
        """
        同步下载文件（在线程池中运行）。
        
        Args:
            remote_path: 远程文件路径
            local_path: 本地文件路径
        """
        # 确保本地目录存在
        local_dir = Path(local_path).parent
        local_dir.mkdir(parents=True, exist_ok=True)
        
        # 下载文件
        self._sftp_client.get(remote_path, local_path)
    
    async def trigger_training(
        self,
        data_yaml_path: str,
        epochs: int = 100,
        batch_size: int = 16,
        img_size: int = 640
    ) -> tuple[int, str, str]:
        """
        触发远程训练任务。
        
        Args:
            data_yaml_path: 数据配置文件路径（远程路径）
            epochs: 训练轮数
            batch_size: 批大小
            img_size: 图像尺寸
            
        Returns:
            (退出码, 标准输出, 标准错误) 元组
        """
        # 构建训练命令
        training_script = f"{settings.remote_yolo_project_path}/{settings.remote_training_script}"
        command = (
            f"cd {settings.remote_yolo_project_path} && "
            f"python {training_script} "
            f"--data {data_yaml_path} "
            f"--epochs {epochs} "
            f"--batch-size {batch_size} "
            f"--img {img_size} "
            f"--weights yolov5s.pt"
        )
        
        logger.info(f"触发远程训练: {command}")
        return await self.execute_command(command, timeout=3600)
    
    async def trigger_inference(
        self,
        model_path: str,
        source_path: str,
        output_path: str,
        conf_threshold: float = 0.25
    ) -> tuple[int, str, str]:
        """
        触发远程推理任务。
        
        Args:
            model_path: 模型权重路径（远程路径）
            source_path: 输入图像路径（远程路径）
            output_path: 输出路径（远程路径）
            conf_threshold: 置信度阈值
            
        Returns:
            (退出码, 标准输出, 标准错误) 元组
        """
        # 构建推理命令
        predict_script = f"{settings.remote_yolo_project_path}/{settings.remote_predict_script}"
        command = (
            f"cd {settings.remote_yolo_project_path} && "
            f"python {predict_script} "
            f"--weights {model_path} "
            f"--source {source_path} "
            f"--output {output_path} "
            f"--conf {conf_threshold}"
        )
        
        logger.info(f"触发远程推理: {command}")
        return await self.execute_command(command, timeout=600)
    
    async def __aenter__(self):
        """异步上下文管理器入口。"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口。"""
        await self.disconnect()

