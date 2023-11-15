from .agent_based_api.v1 import *
from .hci_helper import parse_multi_list

def discovery(section):
    """ Discovery """
    yield Service()

def check(section, metrics):
    """ Check """

    for line in section:
        metric = line['MetricId'].split('=')[0].split(',')[0].split('.',1)[1:][0]
        metric_readable = metric.replace('.', " ")
        if metric not in metrics:
            continue

        value = float(line['Value'])
        value_readable = metrics[metric]['render'](value)

        state = State.OK
        yield Result(
            state = state,
            summary = f"{metric_readable}: {value_readable}",
        )
        yield Metric(
            name = metric.replace('.', '_').lower(),
            value = value
        )


def check_normal(section):
    """
    Not Cluster Mode
    """

    metrics = {
        'IOPS.Read' : {'render': render.timespan },
        'IOPS.Total' : {'render': render.timespan },
        'IOPS.Write' : {'render': render.timespan },
        'Latency.Average' : {'render': render.timespan},
        'Latency.Read' : {'render': render.timespan},
        'Latency.Write' : {'render': render.timespan},
        'Size.Available' : {'render': render.bytes},
        'Size.Total' : {'render': render.bytes},
        'Throughput.Read' : {'render': render.iobandwidth},
        'Throughput.Total' : {'render': render.iobandwidth},
        'Throughput.Write' : {'render': render.iobandwidth},
    }
    yield from check(section, metrics)

def check_cluster(section):
    """
    Cluster Mode
    """

    metrics = {
        'IOPS.Read' : {'render': render.timespan },
        'IOPS.Total' : {'render': render.timespan },
        'IOPS.Write' : {'render': render.timespan },
        'Latency.Average' : {'render': render.timespan},
        'Latency.Read' : {'render': render.timespan},
        'Latency.Write' : {'render': render.timespan},
        'Throughput.Read' : {'render': render.iobandwidth},
        'Throughput.Total' : {'render': render.iobandwidth},
        'Throughput.Write' : {'render': render.iobandwidth},
        'CsvCache.Iops.Read.Hit' : {'render': render.timespan},
        'CsvCache.Iops.Read.HitRate' : {'render': render.percent},
        'CsvCache.Iops.Read.Miss' : {'render': render.timespan},
    }
    yield from check(section, metrics)


register.agent_section(
    name="hci_s2d_volume_performance",
    parse_function=lambda string_table: parse_multi_list(string_table),
)

register.agent_section(
    name="hci_cluster_performance",
    parse_function=lambda string_table: parse_multi_list(string_table),
)

register.check_plugin(
    name="hci_s2d_volume_performance",
    service_name="Storage Pool Performance",
    discovery_function=discovery,
    check_function=check_normal,
)

register.check_plugin(
    name="hci_cluster_performance",
    service_name="Storage Pool Performance",
    discovery_function=discovery,
    check_function=check_cluster,
)
