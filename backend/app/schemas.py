"""Pydantic models for the editable, structured resume used by /api/parse and /api/export."""
from typing import Optional
from pydantic import BaseModel, Field


class Contact(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""
    location: str = ""


class SkillCategory(BaseModel):
    category: str
    skills: list[str] = Field(default_factory=list)


class ExperienceEntry(BaseModel):
    title: str = ""
    company: str = ""
    dates: str = ""
    bullets: list[str] = Field(default_factory=list)


class EducationEntry(BaseModel):
    degree: str = ""
    institution: str = ""
    dates: str = ""


class ProjectEntry(BaseModel):
    title: str = ""
    bullets: list[str] = Field(default_factory=list)


class ResumeData(BaseModel):
    contact: Contact = Field(default_factory=Contact)
    summary: str = ""
    skill_categories: list[SkillCategory] = Field(default_factory=list)
    experience: list[ExperienceEntry] = Field(default_factory=list)
    education: list[EducationEntry] = Field(default_factory=list)
    projects: list[ProjectEntry] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)


class ExportRequest(BaseModel):
    resume: ResumeData
    format: str = "pdf"  # "pdf" | "docx"
