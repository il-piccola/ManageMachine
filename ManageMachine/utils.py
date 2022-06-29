import os
import datetime
import pandas as pd
from zoneinfo import ZoneInfo
from django.db.models import Q
from ManageMachine.settings import *
from ManageMachine.models import Csv, Machine, MachineTime, Schedule

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

def getMachineId(name) :
    return Machine.objects.get(name=name).id

def getMachineIdList(namelist) :
    return list(map(getMachineId, namelist))

def isMachineExists(name) :
    return Machine.objects.filter(name=name).exists()

def fromDawnTillDuskD(date) :
    machinetimes = MachineTime.objects.filter(weekday=date.weekday()).order_by('start')
    if (machinetimes.count() <= 0) :
        return []
    first = machinetimes.first()
    last = machinetimes.last()
    start = date.replace(hour=first.start.hour, minute=first.start.minute)
    start = start.astimezone(ZoneInfo('Asia/Tokyo'))
    end = date.replace(hour=last.end.hour, minute=last.end.minute)
    end = end.astimezone(ZoneInfo('Asia/Tokyo'))
    return [start, end]

def fromDawnTillDuskSE(start, end) :
    slist = fromDawnTillDuskD(start)
    if (len(slist)) <= 0 :
        slist.append(start.replace(hour=0, minute=0, second=0))
    elist = fromDawnTillDuskD(end)
    if (len(elist)) <= 0 :
        elist.append(start)
        elist.append(end.replace(hour=23, minute=59, second=59))
    return [slist[0], elist[1]]

def isReservedDate(machine, order, branch, date) :
    q = Q()
    q.add(Q(machine=machine), Q.AND)
    q.add(~Q(order=order), Q.AND)
    q.add(~Q(branch=branch), Q.AND)
    q.add(Q(start__lt=date), Q.AND)
    q.add(Q(end__gt=date), Q.AND)
    schedules = Schedule.objects.filter(q)
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
    ret = getStartTimeOfDate(start)
    while True :
        end = ret + minutes
        time = fromDawnTillDuskD(ret)
        if (end > time[1]) :
            ret = getStartTimeOfDate(end)
            end = ret + minutes
        schedules = getSchedulesInTerm(machine, ret, end)
        if (schedules.count() <= 0) :
            break
        ret = convertDateTimeAware(schedules.order_by('end').last().end)
    return ret

def getStartTimeOfDate(date) :
    ret = date
    machinetimes = MachineTime.objects.filter(weekday=ret.weekday())
    if (machinetimes.count() <= 0) :
        while (machinetimes.count() <= 0) :
            ret = getNextDay(ret)
            machinetimes = MachineTime.objects.filter(weekday=ret.weekday())
        ret = fromDawnTillDuskD(ret)[0]
    elif (ret > fromDawnTillDuskD(ret)[1]) :
        ret = getNextDay(ret)
        ret = getStartTimeOfDate(ret)
    elif (ret < fromDawnTillDuskD(ret)[0]) :
        ret = fromDawnTillDuskD(ret)[0]
    return ret

def getSchedulesInTerm(machine, start, end) :
    s = convertDateTimeNative(start)
    e = convertDateTimeNative(end)
    q1 = Q()
    q1.add(Q(machine=machine), Q.AND)
    q1.add(Q(start__lte=s), Q.AND)
    q1.add(Q(end__gt=s), Q.AND)
    q2 = Q()
    q2.add(Q(machine=machine), Q.AND)
    q2.add(Q(start__lt=e), Q.AND)
    q2.add(Q(end__gte=e), Q.AND)
    q3 = Q()
    q3.add(Q(machine=machine), Q.AND)
    q3.add(Q(start__gte=s), Q.AND)
    q3.add(Q(end__lte=e), Q.AND)
    schedules1 = Schedule.objects.filter(q1)
    schedules2 = Schedule.objects.filter(q2)
    schedules3 = Schedule.objects.filter(q3)
    return (schedules1|schedules2|schedules3)

def convertDateTimeAware(date) :
    return datetime.datetime(
        date.year,
        date.month,
        date.day,
        date.hour,
        date.minute,
        tzinfo=ZoneInfo('Asia/Tokyo')
    )

def convertDateTimeNative(date) :
    return datetime.datetime(
        date.year,
        date.month,
        date.day,
        date.hour,
        date.minute
    )

def getNextDay(date) :
    return (date + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0)
