"""
=============================================================
 SMART RESUME ANALYZER — DATABASE (MongoDB via Motor)
=============================================================

"""

import os
from datetime import datetime
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME   = os.getenv("DB_NAME",   "resume_analyzer")

_in_memory_store: Dict[str, Dict] = {}   # fallback storage
_mongo_available = False
_db = None

try:
    from motor.motor_asyncio import AsyncIOMotorClient
    _client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=2000)
    _db = _client[DB_NAME]
    _mongo_available = True
    print(f"  MongoDB configured: {MONGO_URL}/{DB_NAME}")
except Exception:
    print("  MongoDB not available — using in-memory storage (demo mode)")


# ─────────────────────────────────────────────────────────────
# CRUD OPERATIONS
# ─────────────────────────────────────────────────────────────

async def save_analysis(analysis_id: str, data: Dict) -> bool:
    
    record = {
        "_id": analysis_id,
        "created_at": datetime.utcnow().isoformat(),
        **data
    }
    
    if _mongo_available and _db is not None:
        try:
            await _db.analyses.replace_one(
                {"_id": analysis_id},
                record,
                upsert=True   # insert if not exists, update if exists
            )
            return True
        except Exception as e:
            print(f"  MongoDB save error: {e} — falling back to memory")
    
    # Fallback: in-memory
    _in_memory_store[analysis_id] = record
    return True


async def get_analysis(analysis_id: str) -> Optional[Dict]:
    """Retrieve a previously saved analysis by ID."""
    if _mongo_available and _db is not None:
        try:
            result = await _db.analyses.find_one({"_id": analysis_id})
            if result:
                result.pop("_id", None)  # remove MongoDB internal field
                return result
        except Exception:
            pass
    
    return _in_memory_store.get(analysis_id)


async def get_recent_analyses(limit: int = 10) -> List[Dict]:
    """Get most recent analyses (for admin/dashboard use)."""
    if _mongo_available and _db is not None:
        try:
            cursor = _db.analyses.find(
                {},
                {"skills_by_category": 0}  # exclude large field
            ).sort("created_at", -1).limit(limit)
            results = await cursor.to_list(length=limit)
            for r in results:
                r.pop("_id", None)
            return results
        except Exception:
            pass
    
    # Fallback
    store_list = list(_in_memory_store.values())
    store_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return store_list[:limit]


async def get_stats() -> Dict:
    """Get aggregate statistics across all analyses."""
    if _mongo_available and _db is not None:
        try:
            total = await _db.analyses.count_documents({})
            pipeline = [
                {"$group": {"_id": None, "avg_score": {"$avg": "$match_percentage"}}}
            ]
            agg = await _db.analyses.aggregate(pipeline).to_list(1)
            avg_score = round(agg[0]["avg_score"], 1) if agg else 0
            return {"total_analyses": total, "avg_match_score": avg_score}
        except Exception:
            pass
    
    scores = [v.get("match_percentage", 0) for v in _in_memory_store.values()]
    return {
        "total_analyses": len(_in_memory_store),
        "avg_match_score": round(sum(scores) / len(scores), 1) if scores else 0,
    }