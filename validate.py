#!/usr/bin/env python3
"""Pre-submission validation script"""

import subprocess
import sys
import json
import os

def validate_openenv():
    """Validate OpenEnv compliance"""
    print("🔍 Validating OpenEnv spec...")
    
    # Check required methods exist
    from environment.core import EmailTriageEnv
    env = EmailTriageEnv()
    
    assert hasattr(env, 'reset'), "Missing reset()"
    assert hasattr(env, 'step'), "Missing step()"
    assert hasattr(env, 'state'), "Missing state()"
    
    print("✅ OpenEnv methods present")
    return True

def validate_tasks():
    """Validate 3+ tasks with graders"""
    print("🔍 Validating tasks...")
    
    from environment.tasks import EasyTriageTask, MediumTriageTask, HardTriageTask
    
    tasks = [EasyTriageTask(), MediumTriageTask(), HardTriageTask()]
    assert len(tasks) >= 3, f"Need 3+ tasks, have {len(tasks)}"
    
    for task in tasks:
        assert hasattr(task, 'grade_action'), f"{task.name} missing grade_action"
        assert hasattr(task, 'compute_final_score'), f"{task.name} missing compute_final_score"
        
        # Test scoring
        score = task.compute_final_score([])
        assert 0 <= score <= 1, f"Score {score} not in [0,1]"
        print(f"  ✅ {task.name}: scoring works")
    
    print("✅ Tasks validated")
    return True

def validate_inference():
    """Validate inference script"""
    print("🔍 Validating inference script...")
    
    # Check inference.py exists
    assert os.path.exists("inference.py"), "inference.py not in root"
    
    # Check for required env vars (just need to exist, can be mock)
    required_vars = ['API_BASE_URL', 'MODEL_NAME']
    for v in required_vars:
        if not os.getenv(v):
            print(f"⚠️ Warning: {v} not set, using mock default")
    
    print("✅ Inference script present")
    return True

def validate_docker():
    """Validate Dockerfile"""
    print("🔍 Validating Dockerfile...")
    assert os.path.exists("Dockerfile"), "Dockerfile missing"
    print("✅ Dockerfile present")
    return True

def main():
    print("="*50)
    print("PRE-SUBMISSION VALIDATION")
    print("="*50)
    
    tests = [
        validate_openenv,
        validate_tasks,
        validate_inference,
        validate_docker
    ]
    
    all_passed = True
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Failed: {e}")
            all_passed = False
    
    print("="*50)
    if all_passed:
        print("✅ ALL VALIDATIONS PASSED!")
        print("\n📋 Ready for submission")
    else:
        print("❌ Some validations failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
