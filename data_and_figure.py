# 安装依赖
# pip install aliyun-python-sdk-cms
# pip install aliyun-python-sdk-ecs
# pip install aliyun-python-sdk-core
# pip install matplotlib

import json
from aliyunsdkcore.client import AcsClient
from aliyunsdkcms.request.v20190101.DescribeExporterOutputListRequest import DescribeExporterOutputListRequest
from aliyunsdkcms.request.v20190101.DescribeMetricMetaListRequest import DescribeMetricMetaListRequest
from aliyunsdkcms.request.v20190101.DescribeMetricListRequest import DescribeMetricListRequest
from aliyunsdkcms.request.v20190101.DescribeProjectMetaRequest import DescribeProjectMetaRequest
import time
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os
from matplotlib.ticker import FuncFormatter
from datetime import datetime, timedelta
server_map = {
      'ProxyServer': 'i-uxxxxxx',
}

client = AcsClient(
   "******",
   "xxxx",
   "cn-shanghai"
)
MetricName = ["cpu_system", "memory_usedutilization", "load_1m"]
instanceid = "i-uf6bzs5dnocyk6cuizig,i-uf6e56zt7ebjroux7lwg,i-uf615k84gwecwb2bz8bd,i-uf6gqdcyg7w4vlswhokf,i-uf6e56zt7ebjroux7hms,i-uf6i5pdzxt7wl8mrwyd6".split(
   ',')

def get_server_monitor(instance, MetricName,end):
   request = DescribeMetricListRequest()
   request.set_accept_format('json')
   request.set_Namespace('acs_ecs_dashboard')
   request.set_MetricName(MetricName)  # cpu_idle
   request.set_EndTime(str(datetime.now())[:19])
   request.set_StartTime(str(datetime.now()-timedelta(minutes=30))[:19])
   response = client.do_action_with_exception(request)
   response = json.loads(str(response, encoding='utf-8'))
   return ([[time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data['timestamp']/1000)), data['Minimum'], data['Maximum'], data['Average'], data["instanceId"]] for data in eval(response["Datapoints"])])


def to_percent(temp, position):
   return '%1.0f' % (temp) + '%'


def get_fig(x, y, name, type):
   plt.figure(figsize=(15, 5))
   plt.title(f"{name} {type}", loc="left")
   if type == 'cpu_system' or type == 'memory_usedutilization':
      plt.ylim((0, 100))
      plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
   else:
      plt.ylim((0, 2))
   for ys in y:
      plt.plot(x, ys)
   plt.ylabel(u'{} USED_RATE'.format(type), fontproperties='SimHei')
   plt.xlabel(u'time', fontproperties='SimHei')
   plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(50))
   plt.grid(True)
   plt.savefig(f'report/{name}_{type}.png')
   plt.close()


if os.path.exists("report") is False:
    os.mkdir("report")

for metric in MetricName:
   datas = get_server_monitor("", metric, "")
   print(len(datas))
   print(datas)
   for isd in server_map:
      server_data = [i for i in datas if i[-1] == server_map[isd]]
      print(server_data)
      x = [i[0] for i in server_data]
      y1, y2, y3 = [i[1] for i in server_data], [i[2] for i in server_data], [i[3] for i in server_data]
      get_fig(x, [y1, y2, y3], isd, metric)
