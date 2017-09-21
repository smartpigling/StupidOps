from flask import g, render_template, url_for, make_response, Response, redirect
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.actions import action
from flask_appbuilder.widgets import ListWidget, ListBlock, ListCarousel, ListItem, ListMasterWidget, \
                                ListLinkWidget, ShowBlockWidget
from flask_appbuilder.models.sqla.filters import FilterStartsWith, FilterEqualFunction
from flask_appbuilder import ModelView, CompactCRUDMixin, MasterDetailView, MultipleView,\
                            expose, has_access, permission_name
from app import appbuilder, db
from .models import Project, ProjectFiles, Module, Problem, ProblemCategory, Solution, Notepad
from .forms import NotepadForm
import datetime

"""
    Create your Views::


    class MyModelView(ModelView):
        datamodel = SQLAInterface(MyModel)


    Next, register your Views::


    appbuilder.add_view(MyModelView, "My View", icon="fa-folder-open-o", category="My Category", category_icon='fa-envelope')
"""

"""
    Application wide 404 error handler
"""
def get_user():
    return g.user

class ProjectFilesModelView(ModelView):
    '''项目文件'''
    datamodel = SQLAInterface(ProjectFiles)

    label_columns = {'file_name': '文件名称', 'download': '下载', 'description': '描述'}
    add_columns = ['file', 'description', 'project']
    edit_columns = ['file', 'description', 'project']
    list_columns = ['file_name', 'download']
    show_columns = ['file_name', 'download']

    list_title = '项目文件'
    add_title = '添加项目文件'


class ProjectModelView(ModelView):
    '''项目配置'''
    datamodel = SQLAInterface(Project)
    related_views = [ProjectFilesModelView]

    show_template = 'appbuilder/general/model/show_cascade.html'
    edit_template = 'appbuilder/general/model/edit_cascade.html'

    label_columns = {'name': '项目名称', 'created_by': '创建人', 'created_on': '创建时间',
                     'changed_by': '修改人', 'changed_on': '修改时间'}
    add_columns = ['name']
    edit_columns = ['name']
    list_columns = ['name', 'created_by', 'created_on', 'changed_by', 'changed_on']
    show_fieldsets = [
        ('基本信息', {'fields': ['name']}),
        ('审计信息', {'fields': ['created_by', 'created_on', 'changed_by', 'changed_on'], 'expanded': False})
    ]

    list_title = '项目列表'
    add_title = '添加项目'
    show_title = '项目详情'
    edit_title = '修改项目'


class ModuleModelView(ModelView):
    '''模块配置'''
    datamodel = SQLAInterface(Module)
    label_columns = {'name': '模块名称'}
    list_columns = ['name']

    list_title = '模块列表'
    add_title = '添加模块'
    show_title = '模块详情'
    edit_title = '修改模块'


class ProblemCategoryModelView(ModelView):
    '''项目问题分类'''
    datamodel = SQLAInterface(ProblemCategory)
    label_columns = {'name': '问题分类名称'}
    list_columns = ['name']

    list_title = '问题分类列表'
    add_title = '问题分类模块'
    show_title = '问题分类详情'
    edit_title = '问题分类模块'


class ProjectMasterView(MasterDetailView):
    '''模块分项目配置'''
    datamodel = SQLAInterface(Project)
    related_views = [ModuleModelView, ProblemCategoryModelView]

    list_template = 'project_master_detail.html'

    label_columns = {'name': '项目名称'}
    list_columns = ['name']

    list_title = '项目列表'
    add_title = '添加项目'
    show_title = '项目详情'
    edit_title = '修改项目'


class SolutionModelView(ModelView):
    '''问题工单处理'''
    datamodel = SQLAInterface(Solution)
    list_widget = ListLinkWidget
    base_filters = [['created_by', FilterEqualFunction, get_user]]

    label_columns = {'description': '处理方法', 'script': '处理脚本', 'problem': '工单问题',
                     'created_by': '处理人', 'created_on': '处理时间'}
    add_columns = ['problem','description', 'script']
    edit_columns = add_columns
    list_columns = ['description', 'script']
    show_fieldsets = [
        ('处理事项', {'fields': ['problem']}),
        ('问题处理', {'fields': ['description', 'script']}),
        ('审计信息', {'fields': ['created_by', 'created_on']})
    ]
    list_title = '工单处理'
    add_title = '添加处理'
    show_title = '处理详情'
    edit_title = '修改处理'

    def post_add_redirect(self):
        _url = self.get_redirect()
        pk = _url.split('/')[-1]
        db.session.query(Problem).filter(Problem.id == pk).one().processed_time = datetime.datetime.now()
        db.session.commit()

        return redirect(_url)


class ProblemModelView(ModelView):
    '''问题工单受理'''
    datamodel = SQLAInterface(Problem)
    related_views = [SolutionModelView]
    list_widget = ListLinkWidget

    label_columns = {'description': '工单描述', 'accepted_time': '接收时间', 'level': '工单情况',
                     'from_person': '发起人', 'from_department': '发起部门', 'from_phone': '联系电话',
                     'problem_category': '工单分类', 'module': '所属模块', 'problem_state': '工单状态'}

    add_columns = ['description', 'level', 'from_person', 'from_department', 'from_phone',
                   'problem_category', 'module']
    edit_columns = add_columns
    list_columns = ['description', 'accepted_time', 'level', 'problem_state']
    show_fieldsets = [
        ('基本信息', {'fields': ['description', 'level', 'accepted_time']}),
        ('工单所属', {'fields': ['module', 'problem_category'], 'expanded': False}),
        ('工单申报', {'fields': ['from_department', 'from_person', 'from_phone'], 'expanded': False})
    ]

    list_title = '工单列表'
    add_title = '添加工单'
    show_title = '工单详情'
    edit_title = '修改工单'

    @action('muldelete', '删除', '确认删除所选?', "fa-trash-o")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


class NotepadListBlock(ListWidget):
    template = 'notepad_list_block.html'


class NotepadModelView(ModelView):
    '''记事本'''
    datamodel = SQLAInterface(Notepad)
    list_widget = NotepadListBlock
    base_filters = [['created_by', FilterEqualFunction, get_user]]

    label_columns = {'context': '内容', 'created_on': '创建时间'}
    add_columns = ['context']
    edit_columns = ['context']
    list_columns = ['context']
    show_fieldsets = [
        ('记录信息', {'fields':['context', 'created_on']})
    ]

    list_title = '记事本'
    add_title = '添加记录'
    show_title = '当前记录'
    edit_title = '修改记录'


@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', base_template=appbuilder.base_template, appbuilder=appbuilder), 404

db.create_all()

appbuilder.add_view_no_menu(ProjectFilesModelView)
appbuilder.add_view_no_menu(ModuleModelView)
appbuilder.add_view_no_menu(ProblemCategoryModelView)

appbuilder.add_view(ProjectModelView,
                    '运维项目',
                    icon='fa-cubes',
                    category='项目配置',
                    category_icon='fa-cog'
                    )

appbuilder.add_view(ProjectMasterView,
                    '项目模块',
                    icon='fa-cube',
                    category='项目配置',
                    category_icon='fa-cog'
                    )

appbuilder.add_view(ProblemModelView,
                    '工单受理',
                    icon='fa-send',
                    category='工单处理',
                    category_icon='fa-share-alt'
                    )

appbuilder.add_view(SolutionModelView,
                    '问题处理',
                    icon='fa-send-o',
                    category='工单处理',
                    category_icon='fa-share-alt'
                    )

appbuilder.add_view(NotepadModelView,
                    '记事本',
                    icon='fa-file-o'
                    )