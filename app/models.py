from flask import g, Markup, url_for
from flask_appbuilder import Model, Base
from flask_appbuilder.filemanager import get_file_original_name
from flask_appbuilder.security.sqla.models import User
from flask_appbuilder.models.mixins import AuditMixin, FileColumn, ImageColumn, BaseMixin
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Enum, DateTime, Text
from sqlalchemy.orm import relationship
import datetime
"""

You can use the extra Flask-AppBuilder fields and Mixin's

AuditMixin will add automatic timestamp of created and modified by who


"""

class Project(AuditMixin, Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True, nullable=False)

    def __repr__(self):
        return self.name


class ProjectFiles(Model):
    id = Column(Integer, primary_key=True)
    file = Column(FileColumn)
    description = Column(String(150))
    project_id = Column(Integer, ForeignKey('project.id'), nullable=False)
    project = relationship('Project')

    def download(self):
        return Markup('<a href="' + url_for('ProjectFilesModelView.download', filename=str(self.file)) + '">Download</a>')

    def file_name(self):
        return get_file_original_name(str(self.file))


class Module(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True, nullable=False)
    project_id = Column(Integer, ForeignKey('project.id'), nullable=False)
    project = relationship('Project')

    def __repr__(self):
        return self.name


class ProblemCategory(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True, nullable=False)
    project_id = Column(Integer, ForeignKey('project.id'), nullable=False)
    project = relationship('Project')

    def __repr__(self):
        return self.name


class Problem(Model):
    id = Column(Integer, primary_key=True)
    description = Column(String(500), nullable=False)
    accepted_time = Column(DateTime, default=datetime.datetime.now, nullable=False)
    processed_time = Column(DateTime)
    level = Column(Enum('不紧急', '一般', '紧急', '非常紧急'))
    from_person = Column(String(50))
    from_department = Column(String(150))
    from_phone = Column(String(11))
    problem_category_id = Column(Integer, ForeignKey('problem_category.id'), nullable=False)
    problem_category = relationship('ProblemCategory')
    module_id = Column(Integer, ForeignKey('module.id'), nullable=False)
    module = relationship('Module')

    def problem_state(self):
        return Markup('<strong>处理完成</strong>' if self.processed_time else '<font color="red">未处理</font>')

    def __repr__(self):
        return self.description


class Solution(AuditMixin, Model):
    id = Column(Integer, primary_key=True)
    description = Column(Text())
    script = Column(Text())
    problem_id = Column(Integer, ForeignKey('problem.id'), nullable=False)
    problem = relationship('Problem')

    def __repr__(self):
        return self.description


class Notepad(AuditMixin, Model):
    id = Column(Integer, primary_key=True)
    context = Column(Text())
