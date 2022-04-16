from .utils import create_excel
from django.shortcuts import render
from django.views import generic  # FormViewを利用するため
from django.contrib.auth.mixins import LoginRequiredMixin   # ログオンユーザのみアクセス可とするために利用する
from django.conf import settings  # settings.pyの定義内容を利用するため
from .forms import UploadForm   # forms.pyで定義したUploadFormをインポート
from django.core.files.storage import default_storage   # ファイルオブジェクト操作のためdefault_storageを利用する
import shutil, os
from django.contrib.auth.decorators import login_required

def top(request):
    return render(request, 'pdfchanging/top.html')

class UploadView(LoginRequiredMixin, generic.FormView):
    form_class = UploadForm
    template_name = 'pdfchanging/upload_form.html'


    def form_valid(self, form):
        user_name = self.request.user.username  #ログオンユーザ名の取得
        user_dir = os.path.join(settings.MEDIA_ROOT, "excel", user_name)   #ユーザディレクトリパスの生成
        if not os.path.isdir(user_dir):  #ユーザディレクトリの作成
            os.makedirs(user_dir)
        temp_dir = form.save()  # upload一時フォルダの取得
        create_excel(temp_dir, user_name)  #PDF->Excelデータ生成
        shutil.rmtree(temp_dir)  #upload一時フォルダの削除
        _, file_list = default_storage.listdir(os.path.join(settings.MEDIA_ROOT, "excel", user_name))
        message = "正常終了しました。"
        context = {
            'file_list': file_list,
            'user_name':user_name,
            'message': message,
        }
        return render(self.request, 'pdfchanging/complete.html', context)


    def form_invalid(self, form):
        return render(self.request, 'pdfchanging/upload_form.html', {'form': form})

class ListView(LoginRequiredMixin, generic.TemplateView):

    template_name = 'pdfchanging/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  #承継元のメソッドを呼び出す
        """自分が作成したExcelファイルだけを一覧表示"""
        login_user_name = self.request.user.username
        file_list = default_storage.listdir(os.path.join(settings.MEDIA_ROOT, "excel", login_user_name))[1]
        context = {
            'file_list': file_list,
            'login_user_name':login_user_name,
            }
        return context


@login_required
def dell_file(request):
    checks_value = request.POST.getlist('checks') #CheckBox＝Onのファイル名を取得
    login_user_name = request.user.username   #ログオンユーザ名を取得

    #Excelファイルの格納パスを取得
    if checks_value:
        for file in checks_value:
            path = os.path.join(settings.MEDIA_ROOT, "excel", login_user_name, file)
            default_storage.delete(path)    #CheckBox=ONのファイルをサーバから削除
        return render(request, 'pdfchanging/delete.html', {'checks_value': checks_value})
    else:
        login_user_name = request.user.username
        file_list = default_storage.listdir(os.path.join(settings.MEDIA_ROOT, "excel", login_user_name))[1]
        warning_message = "削除対象ファイルが選択されていません。"

        context = {
            'file_list': file_list,
            'login_user_name':login_user_name,
            'warning_message': warning_message,
        }
        return render(request, 'pdfchanging/list.html',context)
