import os
import datetime
from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from ManageMachine.settings import *

def getUploadPath(instance, filename) :
    newname = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_') + filename
    return os.path.join('csv', newname)

class Csv(models.Model) :
    csv = models.FileField(upload_to=getUploadPath, validators=[FileExtensionValidator(['csv'])])
    time = models.DateTimeField(default=timezone.now)

    def getpath(self) :
        return os.path.join(MEDIA_ROOT, self.csv.path)

class Machine(models.Model) :
    name = models.CharField('号機名', max_length=255, null=False, blank=False)
    
    def __str__(self) :
        return self.name

class MachineTime(models.Model) :
    machine = models.ForeignKey(Machine, on_delete=models.DO_NOTHING)
    weekday = models.IntegerField()
    start = models.TimeField()
    end = models.TimeField()
    
    def getWeekdayName(self) :
        return WEEKDAY_NAME[self.weekday]

class Schedule(models.Model) :
    machine = models.ForeignKey(Machine, on_delete=models.DO_NOTHING, null=False)
    order = models.CharField('受注番号', max_length=255, null=True, blank=True)
    branch = models.IntegerField('枝番号', null=True, blank=True)
    start = models.DateTimeField('開始日時', null=False)
    end = models.DateTimeField('終了日時', null=False)

class User(models.Model) :
    userid = models.CharField('ユーザID', max_length=255)
    password = models.CharField('パスワード', max_length=255)
    name = models.CharField('表示名', max_length=255)
    email = models.EmailField('メールアドレス', max_length=255)
    admin = models.BooleanField('管理者フラグ')
