# jenkins_param_validator/validators.py
from typing import Any, Dict


def validate_deployment_rules(data: Dict[str, Any], schema: Dict[str, Any]):
    """Validate deployment-specific rules"""
    
    # Production deployment requires explicit flag
    if data.get("ENV") == "prod" and not data.get("ALLOW_PROD_DEPLOY"):
        raise ValueError("Production deployment requires ALLOW_PROD_DEPLOY=true")
    
    # Production requires resource limits
    if data.get("ENV") == "prod":
        if not data.get("CPU_LIMIT") or not data.get("MEMORY_LIMIT"):
            raise ValueError("Production deployments must specify CPU_LIMIT and MEMORY_LIMIT")


def validate_resource_limits(data: Dict[str, Any], schema: Dict[str, Any]):
    """Validate resource limit compatibility"""
    
    # If both replicas and memory are set, check total memory
    replicas = data.get("REPLICAS", 1)
    memory = data.get("MEMORY_LIMIT", "")
    
    if memory.endswith("Mi"):
        mem_value = int(memory[:-2])
        total_memory = replicas * mem_value
        
        if total_memory > 10240:  # Max 10GB total
            raise ValueError(f"Total memory ({total_memory}Mi) exceeds 10GB limit")