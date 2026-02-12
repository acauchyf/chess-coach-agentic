from __future__ import annotations
from fastapi import APIRouter
from chess_coach.api.deps import get_llm
from chess_coach.application.course_generator import generate_course, course_to_dict

router = APIRouter(tags=["courses"])

@router.get("/courses/course")
def get_course(topic: str):
    llm = get_llm()
    c = generate_course(topic, llm=llm)
    return course_to_dict(c)
