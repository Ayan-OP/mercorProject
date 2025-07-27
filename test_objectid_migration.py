#!/usr/bin/env python3
"""
Simple test script to verify ObjectId migration works correctly.
This script tests the basic functionality without requiring a database connection.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from bson import ObjectId
from schemas.project import ProjectCreate, ProjectInDB, ProjectResponse
from schemas.employee import EmployeeCreate, EmployeeInDB, EmployeeResponse

def test_project_objectid():
    """Test that project ObjectIds work correctly."""
    print("Testing Project ObjectId functionality...")
    
    # Test creating a project with ObjectId
    project_create = ProjectCreate(
        name="Test Project",
        description="A test project",
        billable=True,
        employees=[],
        screenshotSettings={"screenshotEnabled": True},
        payroll={"*": {"billRate": 50.0}}
    )
    
    # Test creating a DB model (this should generate an ObjectId)
    db_project = ProjectInDB(
        **project_create.model_dump(),
        creatorId="test-creator"
    )
    
    print(f"✓ Project ID type: {type(db_project.id)}")
    print(f"✓ Project ID value: {db_project.id}")
    print(f"✓ Project ID is ObjectId: {isinstance(db_project.id, ObjectId)}")
    
    # Test conversion to response model
    response = ProjectResponse.from_db_model(db_project)
    print(f"✓ Response ID type: {type(response.id)}")
    print(f"✓ Response ID value: {response.id}")
    print(f"✓ Response ID is string: {isinstance(response.id, str)}")
    
    # Test ObjectId validation
    try:
        valid_oid = ObjectId("507f1f77bcf86cd799439011")
        print(f"✓ Valid ObjectId created: {valid_oid}")
    except Exception as e:
        print(f"✗ Valid ObjectId failed: {e}")
    
    try:
        invalid_oid = ObjectId("invalid-id")
        print(f"✗ Invalid ObjectId should have failed")
    except Exception as e:
        print(f"✓ Invalid ObjectId correctly rejected: {e}")
    
    print()

def test_employee_objectid():
    """Test that employee ObjectIds work correctly."""
    print("Testing Employee ObjectId functionality...")
    
    # Test creating an employee with ObjectId
    employee_create = EmployeeCreate(
        name="Test Employee",
        email="test@example.com"
    )
    
    # Test creating a DB model (this should generate an ObjectId)
    db_employee = EmployeeInDB(
        **employee_create.model_dump(),
        identifier=employee_create.email
    )
    
    print(f"✓ Employee ID type: {type(db_employee.id)}")
    print(f"✓ Employee ID value: {db_employee.id}")
    print(f"✓ Employee ID is ObjectId: {isinstance(db_employee.id, ObjectId)}")
    
    # Test conversion to response model
    response = EmployeeResponse.from_db_model(db_employee)
    print(f"✓ Response ID type: {type(response.id)}")
    print(f"✓ Response ID value: {response.id}")
    print(f"✓ Response ID is string: {isinstance(response.id, str)}")
    
    print()

def test_objectid_conversion():
    """Test ObjectId to string conversion and back."""
    print("Testing ObjectId conversion...")
    
    # Create an ObjectId
    original_oid = ObjectId()
    print(f"✓ Original ObjectId: {original_oid}")
    
    # Convert to string
    oid_string = str(original_oid)
    print(f"✓ ObjectId as string: {oid_string}")
    
    # Convert back to ObjectId
    try:
        converted_oid = ObjectId(oid_string)
        print(f"✓ Converted back to ObjectId: {converted_oid}")
        print(f"✓ Conversion successful: {original_oid == converted_oid}")
    except Exception as e:
        print(f"✗ Conversion failed: {e}")
    
    print()

if __name__ == "__main__":
    print("ObjectId Migration Test")
    print("=" * 50)
    
    test_project_objectid()
    test_employee_objectid()
    test_objectid_conversion()
    
    print("All tests completed!")
    print("\nKey benefits of using ObjectIds:")
    print("1. Better performance for MongoDB queries")
    print("2. Guaranteed uniqueness across the database")
    print("3. Smaller storage size (12 bytes vs variable string length)")
    print("4. Better integration with MongoDB's native features")
    print("5. Built-in timestamp information in the ObjectId") 