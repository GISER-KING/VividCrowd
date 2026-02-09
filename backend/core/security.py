"""
数据加密与隐私保护模块
"""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
from typing import Optional


class DataEncryption:
    """数据加密工具类"""

    def __init__(self, encryption_key: Optional[str] = None):
        """
        初始化加密工具

        Args:
            encryption_key: 加密密钥（如果不提供，将从环境变量读取）
        """
        if encryption_key:
            self.key = encryption_key.encode()
        else:
            # 从环境变量读取或生成新密钥
            self.key = os.getenv('ENCRYPTION_KEY', self._generate_key()).encode()

        # 使用PBKDF2派生密钥
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'vividcrowd_salt',  # 在生产环境应使用随机salt
            iterations=100000,
            backend=default_backend()
        )
        derived_key = base64.urlsafe_b64encode(kdf.derive(self.key))
        self.cipher = Fernet(derived_key)

    @staticmethod
    def _generate_key() -> str:
        """生成新的加密密钥"""
        return Fernet.generate_key().decode()

    def encrypt(self, data: str) -> str:
        """
        加密数据

        Args:
            data: 要加密的字符串

        Returns:
            加密后的字符串（Base64编码）
        """
        if not data:
            return data

        encrypted = self.cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """
        解密数据

        Args:
            encrypted_data: 加密的字符串（Base64编码）

        Returns:
            解密后的原始字符串
        """
        if not encrypted_data:
            return encrypted_data

        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"解密失败: {str(e)}")

    def encrypt_dict(self, data: dict, fields: list) -> dict:
        """
        加密字典中的指定字段

        Args:
            data: 数据字典
            fields: 需要加密的字段列表

        Returns:
            加密后的字典
        """
        encrypted_data = data.copy()
        for field in fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt(str(encrypted_data[field]))
        return encrypted_data

    def decrypt_dict(self, data: dict, fields: list) -> dict:
        """
        解密字典中的指定字段

        Args:
            data: 数据字典
            fields: 需要解密的字段列表

        Returns:
            解密后的字典
        """
        decrypted_data = data.copy()
        for field in fields:
            if field in decrypted_data and decrypted_data[field]:
                try:
                    decrypted_data[field] = self.decrypt(decrypted_data[field])
                except:
                    pass  # 如果解密失败，保持原值
        return decrypted_data


class DataMasking:
    """数据脱敏工具类"""

    @staticmethod
    def mask_phone(phone: str) -> str:
        """
        手机号脱敏

        Args:
            phone: 手机号

        Returns:
            脱敏后的手机号（如：138****5678）
        """
        if not phone or len(phone) < 11:
            return phone
        return phone[:3] + "****" + phone[-4:]

    @staticmethod
    def mask_email(email: str) -> str:
        """
        邮箱脱敏

        Args:
            email: 邮箱地址

        Returns:
            脱敏后的邮箱（如：abc***@example.com）
        """
        if not email or '@' not in email:
            return email
        parts = email.split('@')
        username = parts[0]
        if len(username) <= 3:
            masked_username = username[0] + "**"
        else:
            masked_username = username[:3] + "***"
        return masked_username + "@" + parts[1]

    @staticmethod
    def mask_id_card(id_card: str) -> str:
        """
        身份证号脱敏

        Args:
            id_card: 身份证号

        Returns:
            脱敏后的身份证号（如：110***********1234）
        """
        if not id_card or len(id_card) < 18:
            return id_card
        return id_card[:3] + "***********" + id_card[-4:]
