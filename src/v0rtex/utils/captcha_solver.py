"""
CAPTCHA solving utilities for v0rtex scraper.
"""

import base64
import time
import requests
from typing import Dict, Optional, Union, Any, List
from abc import ABC, abstractmethod
from loguru import logger
from PIL import Image
import io


class CaptchaSolverBase(ABC):
    """Base class for CAPTCHA solvers."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.service_name = self.__class__.__name__
    
    @abstractmethod
    def solve_recaptcha(self, site_key: str, url: str) -> Optional[str]:
        """Solve reCAPTCHA."""
        pass
    
    @abstractmethod
    def solve_hcaptcha(self, site_key: str, url: str) -> Optional[str]:
        """Solve hCaptcha."""
        pass
    
    @abstractmethod
    def solve_image_captcha(self, image_data: Union[str, bytes]) -> Optional[str]:
        """Solve image CAPTCHA."""
        pass


class TwoCaptchaSolver(CaptchaSolverBase):
    """2captcha.com CAPTCHA solver."""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://2captcha.com/in.php"
        self.result_url = "https://2captcha.com/res.php"
    
    def solve_recaptcha(self, site_key: str, url: str) -> Optional[str]:
        """Solve reCAPTCHA using 2captcha."""
        try:
            # Submit CAPTCHA
            submit_data = {
                "key": self.api_key,
                "method": "userrecaptcha",
                "googlekey": site_key,
                "pageurl": url,
                "json": 1
            }
            
            response = requests.post(self.base_url, data=submit_data)
            result = response.json()
            
            if result.get("status") == 1:
                captcha_id = result["request"]
                
                # Wait for solution
                for _ in range(60):  # Wait up to 5 minutes
                    time.sleep(5)
                    
                    check_data = {
                        "key": self.api_key,
                        "action": "get",
                        "id": captcha_id,
                        "json": 1
                    }
                    
                    check_response = requests.get(self.result_url, params=check_data)
                    check_result = check_response.json()
                    
                    if check_result.get("status") == 1:
                        return check_result["request"]
                    elif check_result.get("request") == "CAPCHA_NOT_READY":
                        continue
                    else:
                        logger.error(f"2captcha error: {check_result}")
                        break
            else:
                logger.error(f"2captcha submission error: {result}")
                
        except Exception as e:
            logger.error(f"2captcha recaptcha solving error: {e}")
        
        return None
    
    def solve_hcaptcha(self, site_key: str, url: str) -> Optional[str]:
        """Solve hCaptcha using 2captcha."""
        try:
            submit_data = {
                "key": self.api_key,
                "method": "hcaptcha",
                "sitekey": site_key,
                "pageurl": url,
                "json": 1
            }
            
            response = requests.post(self.base_url, data=submit_data)
            result = response.json()
            
            if result.get("status") == 1:
                captcha_id = result["request"]
                
                # Wait for solution
                for _ in range(60):
                    time.sleep(5)
                    
                    check_data = {
                        "key": self.api_key,
                        "action": "get",
                        "id": captcha_id,
                        "json": 1
                    }
                    
                    check_response = requests.get(self.result_url, params=check_data)
                    check_result = check_response.json()
                    
                    if check_result.get("status") == 1:
                        return check_result["request"]
                    elif check_result.get("request") == "CAPCHA_NOT_READY":
                        continue
                    else:
                        logger.error(f"2captcha hcaptcha error: {check_result}")
                        break
            else:
                logger.error(f"2captcha hcaptcha submission error: {result}")
                
        except Exception as e:
            logger.error(f"2captcha hcaptcha solving error: {e}")
        
        return None
    
    def solve_image_captcha(self, image_data: Union[str, bytes]) -> Optional[str]:
        """Solve image CAPTCHA using 2captcha."""
        try:
            # Convert image to base64 if needed
            if isinstance(image_data, bytes):
                image_base64 = base64.b64encode(image_data).decode('utf-8')
            else:
                image_base64 = image_data
            
            submit_data = {
                "key": self.api_key,
                "method": "base64",
                "body": image_base64,
                "json": 1
            }
            
            response = requests.post(self.base_url, data=submit_data)
            result = response.json()
            
            if result.get("status") == 1:
                captcha_id = result["request"]
                
                # Wait for solution
                for _ in range(30):  # Wait up to 2.5 minutes
                    time.sleep(5)
                    
                    check_data = {
                        "key": self.api_key,
                        "action": "get",
                        "id": captcha_id,
                        "json": 1
                    }
                    
                    check_response = requests.get(self.result_url, params=check_data)
                    check_result = check_response.json()
                    
                    if check_result.get("status") == 1:
                        return check_result["request"]
                    elif check_result.get("request") == "CAPCHA_NOT_READY":
                        continue
                    else:
                        logger.error(f"2captcha image error: {check_result}")
                        break
            else:
                logger.error(f"2captcha image submission error: {result}")
                
        except Exception as e:
            logger.error(f"2captcha image solving error: {e}")
        
        return None


class AntiCaptchaSolver(CaptchaSolverBase):
    """AntiCaptcha.com CAPTCHA solver."""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://api.anti-captcha.com"
    
    def solve_recaptcha(self, site_key: str, url: str) -> Optional[str]:
        """Solve reCAPTCHA using AntiCaptcha."""
        try:
            # Submit CAPTCHA
            submit_data = {
                "clientKey": self.api_key,
                "task": {
                    "type": "RecaptchaV2TaskProxyless",
                    "websiteURL": url,
                    "websiteKey": site_key
                }
            }
            
            response = requests.post(f"{self.base_url}/createTask", json=submit_data)
            result = response.json()
            
            if result.get("errorId") == 0:
                task_id = result["taskId"]
                
                # Wait for solution
                for _ in range(60):
                    time.sleep(5)
                    
                    check_data = {
                        "clientKey": self.api_key,
                        "taskId": task_id
                    }
                    
                    check_response = requests.post(f"{self.base_url}/getTaskResult", json=check_data)
                    check_result = check_response.json()
                    
                    if check_result.get("status") == "ready":
                        return check_result["solution"]["gRecaptchaResponse"]
                    elif check_result.get("status") == "processing":
                        continue
                    else:
                        logger.error(f"AntiCaptcha error: {check_result}")
                        break
            else:
                logger.error(f"AntiCaptcha submission error: {result}")
                
        except Exception as e:
            logger.error(f"AntiCaptcha recaptcha solving error: {e}")
        
        return None
    
    def solve_hcaptcha(self, site_key: str, url: str) -> Optional[str]:
        """Solve hCaptcha using AntiCaptcha."""
        try:
            submit_data = {
                "clientKey": self.api_key,
                "task": {
                    "type": "HCaptchaTaskProxyless",
                    "websiteURL": url,
                    "websiteKey": site_key
                }
            }
            
            response = requests.post(f"{self.base_url}/createTask", json=submit_data)
            result = response.json()
            
            if result.get("errorId") == 0:
                task_id = result["taskId"]
                
                # Wait for solution
                for _ in range(60):
                    time.sleep(5)
                    
                    check_data = {
                        "clientKey": self.api_key,
                        "taskId": task_id
                    }
                    
                    check_response = requests.post(f"{self.base_url}/getTaskResult", json=check_data)
                    check_result = check_response.json()
                    
                    if check_result.get("status") == "ready":
                        return check_result["solution"]["gRecaptchaResponse"]
                    elif check_result.get("status") == "processing":
                        continue
                    else:
                        logger.error(f"AntiCaptcha hcaptcha error: {check_result}")
                        break
            else:
                logger.error(f"AntiCaptcha hcaptcha submission error: {result}")
                
        except Exception as e:
            logger.error(f"AntiCaptcha hcaptcha solving error: {e}")
        
        return None
    
    def solve_image_captcha(self, image_data: Union[str, bytes]) -> Optional[str]:
        """Solve image CAPTCHA using AntiCaptcha."""
        try:
            # Convert image to base64 if needed
            if isinstance(image_data, bytes):
                image_base64 = base64.b64encode(image_data).decode('utf-8')
            else:
                image_base64 = image_data
            
            submit_data = {
                "clientKey": self.api_key,
                "task": {
                    "type": "ImageToTextTask",
                    "body": image_base64
                }
            }
            
            response = requests.post(f"{self.base_url}/createTask", json=submit_data)
            result = response.json()
            
            if result.get("errorId") == 0:
                task_id = result["taskId"]
                
                # Wait for solution
                for _ in range(30):
                    time.sleep(5)
                    
                    check_data = {
                        "clientKey": self.api_key,
                        "taskId": task_id
                    }
                    
                    check_response = requests.post(f"{self.base_url}/getTaskResult", json=check_data)
                    check_result = check_response.json()
                    
                    if check_result.get("status") == "ready":
                        return check_result["solution"]["text"]
                    elif check_result.get("status") == "processing":
                        continue
                    else:
                        logger.error(f"AntiCaptcha image error: {check_result}")
                        break
            else:
                logger.error(f"AntiCaptcha image submission error: {result}")
                
        except Exception as e:
            logger.error(f"AntiCaptcha image solving error: {e}")
        
        return None


class CaptchaSolver:
    """Main CAPTCHA solver that manages multiple services."""
    
    def __init__(self, api_keys: Dict[str, str]):
        self.solvers = {}
        self.api_keys = api_keys
        
        # Initialize available solvers
        if "2captcha" in api_keys:
            self.solvers["2captcha"] = TwoCaptchaSolver(api_keys["2captcha"])
        
        if "anticaptcha" in api_keys:
            self.solvers["anticaptcha"] = AntiCaptchaSolver(api_keys["anticaptcha"])
    
    def solve_recaptcha(self, site_key: str, url: str, service: str = None) -> Optional[str]:
        """Solve reCAPTCHA using specified or available service."""
        if service and service in self.solvers:
            return self.solvers[service].solve_recaptcha(site_key, url)
        
        # Try available services
        for solver_name, solver in self.solvers.items():
            try:
                result = solver.solve_recaptcha(site_key, url)
                if result:
                    logger.info(f"Solved reCAPTCHA using {solver_name}")
                    return result
            except Exception as e:
                logger.error(f"Failed to solve reCAPTCHA with {solver_name}: {e}")
        
        return None
    
    def solve_hcaptcha(self, site_key: str, url: str, service: str = None) -> Optional[str]:
        """Solve hCaptcha using specified or available service."""
        if service and service in self.solvers:
            return self.solvers[service].solve_hcaptcha(site_key, url)
        
        # Try available services
        for solver_name, solver in self.solvers.items():
            try:
                result = solver.solve_hcaptcha(site_key, url)
                if result:
                    logger.info(f"Solved hCaptcha using {solver_name}")
                    return result
            except Exception as e:
                logger.error(f"Failed to solve hCaptcha with {solver_name}: {e}")
        
        return None
    
    def solve_image_captcha(self, image_data: Union[str, bytes], service: str = None) -> Optional[str]:
        """Solve image CAPTCHA using specified or available service."""
        if service and service in self.solvers:
            return self.solvers[service].solve_image_captcha(image_data)
        
        # Try available services
        for solver_name, solver in self.solvers.items():
            try:
                result = solver.solve_image_captcha(image_data)
                if result:
                    logger.info(f"Solved image CAPTCHA using {solver_name}")
                    return result
            except Exception as e:
                logger.error(f"Failed to solve image CAPTCHA with {solver_name}: {e}")
        
        return None
    
    def get_available_services(self) -> List[str]:
        """Get list of available CAPTCHA solving services."""
        return list(self.solvers.keys())
    
    def get_service_status(self) -> Dict[str, bool]:
        """Get status of all CAPTCHA solving services."""
        return {name: True for name in self.solvers.keys()}
