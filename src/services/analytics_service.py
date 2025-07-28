from typing import List, Optional, Dict, Any
from datetime import datetime

from db.mongo import get_db
from schemas.analytics import ProjectTime, TaskTime

async def get_project_time_analytics(
    start: int,
    end: int,
    employee_id: Optional[str] = None,
    project_id: Optional[str] = None,
    task_id: Optional[str] = None
) -> List[ProjectTime]:
    """
    Calculates the total time, costs, and income for projects within a given
    date range using a MongoDB aggregation pipeline.
    """
    start_dt = datetime.fromtimestamp(start / 1000.0)
    end_dt = datetime.fromtimestamp(end / 1000.0)

    # 1. Build the initial matching stage for the pipeline
    match_stage: Dict[str, Any] = {
        "$match": {
            "startTime": {"$gte": start_dt},
            "endTime": {"$lte": end_dt}
        }
    }
    # Add optional filters
    if employee_id:
        match_stage["$match"]["employeeId"] = employee_id
    if project_id:
        match_stage["$match"]["projectId"] = project_id
    if task_id:
        match_stage["$match"]["taskId"] = task_id

    # 2. Build the grouping and calculation stage
    group_stage = {
        "$group": {
            "_id": "$projectId",
            "totalTimeMillis": {
                "$sum": {
                    "$subtract": ["$end", "$start"]
                }
            },
            # Assuming billRate is per hour, we calculate income
            "totalIncome": {
                "$sum": {
                    "$multiply": [
                        {"$divide": [{"$subtract": ["$end", "$start"]}, 3600000]}, # Duration in hours
                        {"$ifNull": ["$billRate", 0]} # Use billRate, default to 0 if null
                    ]
                }
            },
            # Assuming payRate is per hour, we calculate costs
            "totalCosts": {
                "$sum": {
                    "$multiply": [
                        {"$divide": [{"$subtract": ["$end", "$start"]}, 3600000]}, # Duration in hours
                        {"$ifNull": ["$payRate", 0]} # Use payRate, default to 0 if null
                    ]
                }
            }
        }
    }

    # 3. Build the final projection stage to format the output
    project_stage = {
        "$project": {
            "_id": 0, # Exclude the default _id field
            "id": "$_id", # Rename _id to id
            "time": "$totalTimeMillis",
            "income": {"$round": ["$totalIncome", 2]}, # Round to 2 decimal places
            "costs": {"$round": ["$totalCosts", 2]}
        }
    }

    # 4. Assemble and run the aggregation pipeline
    db = await get_db()
    pipeline = [match_stage, group_stage, project_stage]
    results = []
    cursor = await db.time_windows.aggregate(pipeline)
    result = await cursor.to_list(length=None)
    
    async for doc in result:
        results.append(ProjectTime(**doc))
        
    return results


async def get_task_time_for_employee(
    employee_id: str,
    task_id: str
) -> Optional[TaskTime]:
    """
    Calculates the total time spent by a specific employee on a specific task.
    """
    db = await get_db()
    pipeline = [
        {
            "$match": {
                "employeeId": employee_id,
                "taskId": task_id
            }
        },
        {
            "$group": {
                "_id": None, # Group all matching documents into one
                "totalTimeMillis": {
                    "$sum": {
                        "$subtract": ["$end", "$start"]
                    }
                }
            }
        }
    ]

    cursor = await db.time_windows.aggregate(pipeline)
    result = await cursor.to_list(length=1)

    if not result:
        # If there are no time entries, return a total of 0
        return TaskTime(employeeId=employee_id, taskId=task_id, totalTimeMillis=0)

    return TaskTime(
        employeeId=employee_id,
        taskId=task_id,
        totalTimeMillis=result[0]["totalTimeMillis"]
    )
