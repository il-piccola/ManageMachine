import os
import datetime
import pandas as pd
from zoneinfo import ZoneInfo
from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.db.models import Max
from ManageMachine.settings import *

def getUploadPath(instance, filename) :
    newname = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_') + filename
    return os.path.join('csv', newname)

class Csv(models.Model) :
    csv = models.FileField(upload_to=getUploadPath, validators=[FileExtensionValidator(['csv'])])
    time = models.DateTimeField(default=timezone.now)

    def getpath(self) :
        return os.path.join(MEDIA_ROOT, self.csv.path)

def saveCsv(form) :
    form.save()
    path = form.instance.getpath()
    if not os.path.exists(path) :
        return ''
    model = Csv.objects.order_by('time')
    for i in range(len(model) - CSV_FILE_REMAIN) :
        model[i].delete()
    return path

def readCsv() :
    models = Csv.objects.all()
    for model in models :
        path = model.getpath()
        if not os.path.exists(path) :
            model.delete()
    if Csv.objects.count() <= 0 :
        return pd.DataFrame()   # Noneを返すと判定エラーが発生するので空のDataFrameを返す
    path = Csv.objects.order_by('time').last().getpath()
    df = pd.read_csv(path, encoding="utf_8", names=CSV_COL_NAME)
    return df

class Machine(models.Model) :
    name = models.CharField('号機名', max_length=255, null=False, blank=False)
    
    def __str__(self) :
        return self.name

def getMachineId(name) :
    return Machine.objects.get(name=name).id

def getMachineIdList(namelist) :
    return list(map(getMachineId, namelist))

def isMachineExists(name) :
    return Machine.objects.filter(name=name).exists()

class MachineTime(models.Model) :
    machine = models.ForeignKey(Machine, on_delete=models.DO_NOTHING)
    weekday = models.IntegerField()
    start = models.TimeField()
    end = models.TimeField()
    
    def getWeekdayName(self) :
        return WEEKDAY_NAME[self.weekday]

def fromDawnTillDuskD(date) :
    start = datetime.datetime.combine(date, datetime.time(hour=0, minute=0, second=0))
    end = start.replace(hour=23, minute=59, second=59)
    machinetimes = MachineTime.objects.filter(weekday=date.weekday()).order_by('start')
    if (machinetimes.count() > 0) :
        first = machinetimes.first()
        last = machinetimes.last()
        start = start.replace(hour=first.start.hour, minute=first.start.minute)
        start = start.astimezone(ZoneInfo('Asia/Tokyo'))
        end = end.replace(hour=last.end.hour, minute=last.end.minute)
        end = end.astimezone(ZoneInfo('Asia/Tokyo'))
    return [start, end]

def fromDawnTillDuskSE(start, end) :
    slist = fromDawnTillDuskD(start)
    elist = fromDawnTillDuskD(end)
    return [slist[0], elist[1]]

class Schedule(models.Model) :
    machine = models.ForeignKey(Machine, on_delete=models.DO_NOTHING, null=False)
    order = models.CharField('受注番号', max_length=255, null=True, blank=True)
    branch = models.IntegerField('枝番号', null=True, blank=True)
    start = models.DateTimeField('開始日時', null=False)
    end = models.DateTimeField('終了日時', null=False)

def isReservedDate(machine, date) :
    schedules = Schedule.objects.filter(machine=machine, start__lt=date, end__gt=date)
    if (schedules.count() > 0) :
        return True
    return False

def resetBranch(order) :
    machines = Machine.objects.all()
    for machine in machines :
        schedules = Schedule.objects.filter(order=order, machine=machine)
        for i, schedule in enumerate(schedules) :
            schedule.branch = i+1
            schedule.save()

def getScheduleTime(machine, start, minutes) :
    ret = start.astimezone(ZoneInfo('Asia/Tokyo'))
    time = fromDawnTillDuskD(ret)
    print('ret', ret, ret.timestamp())
    print('time', time[0], time[0].timestamp())
    if (ret.timestamp() < time[0].timestamp()) :   # そのままでは比較できないのでtimestamp()を使用
        ret = time[0]
    schedules = Schedule.objects.filter(machine=machine)
    while True :
        end = (ret + minutes).astimezone(ZoneInfo('Asia/Tokyo'))
        time = fromDawnTillDuskD(ret)
        if (end.timestamp() > time[1].timestamp()) :
            print('end', end, end.timestamp())
            print('time', time[1], time[1].timestamp())
            ret = fromDawnTillDuskD(ret + datetime.timedelta(days=1))[0]
            end = ret + minutes
        schedules = Schedule.objects.filter(machine=machine, start__gte=start, end__lte=end).order_by('start')
        if (schedules.count() <= 0) :
            break
        ret = schedules.first().end
    return ret
