import argparse
import pathlib
import json
from tqdm import tqdm
import json
import numpy

import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_bar_with_outliers(datas, names):
    start = 1e-10
    # end = data.max() / 2
    end = 1
    nbins = 11

    # Making a histogram
    # largest_value = data.max()
    # bins = numpy.geomspace(start, largest_value, nbins).tolist() #+ [largest_value]
    bins = numpy.geomspace(start, end, nbins).tolist() #+ [largest_value]
    bins = [0] + bins
    # assert(data.min() > 0)
    # bins = [start]
    # i = 0
    # while bins[-1] < end:
    #     # bins.append(bins[-1] * (5 if i % 2 == 0 else 2))
    #     bins.append(bins[-1] * 5)
    #     i += 1
    # bins[0] = start
    # if bins[-1] > largest_value:
    #     bins[-1] = largest_value
    # else:
    #     bins.append(largest_value)
    # print(bins)
    hists = [numpy.histogram(data, bins=bins) for data in datas]

    # Adding labels to the chart
    labels = []
    for i, j in zip(hists[0][1][0::1], hists[0][1][1::1]):
        # if i <= start:
        #     labels.append('< {:.0e}'.format(j))
        if j <= end:
            if i == 0:
                labels.append('[{:g}, {:.0e})'.format(i, j))
            elif j == 1:
                labels.append('[{:.0e}, {:g}]'.format(i, j))
            else:
                labels.append('[{:.0e}, {:.0e})'.format(i, j))
        else:
            labels.append('> {:.0e}'.format(i))

    # Plotting the graph 
    rows, cols = 1, 5
    fig = make_subplots(rows=1, cols=5, shared_yaxes=True)

    # for i, (hist, data, name) in enumerate(zip(hists, datas, names)):
    #     fig.add_trace(
    #         go.Bar(x=labels, y=100 * hist[0] / data.size, name=name),
    #         row=i//cols + 1, col=i%cols + 1)

    fig = go.Figure(data=[
        go.Bar(x=labels, y=100 * hist[0] / data.size, name=name)
        for hist, data, name in zip(hists, datas, names)
    ])

    fig.update_layout(
        title_x=0.5,
        xaxis_title="error in time of impact computation",
        # yaxis_title="percentage",
        # template="plotly_white",
        # margin=dict(l=0, r=0, b=0, t=10),
        width=cols*250,
        height=rows*750,
        yaxis={
            "ticksuffix": "%",
            "gridcolor": "rgba(0,0,0,0.4)",
            "linecolor": "black",
            "ticks": "outside",
            "range": (0, 100)
        },
        xaxis={
            "ticksuffix": "",
            "showexponent": "all",
            "exponentformat": "e",
            "linecolor": "black",
            "showline": True,
            "ticks": "outside"
        },
        bargap=0,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(size=28, color="black", family="times"),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor="rgba(0,0,0,0)"
        )
    )

    return fig

def main():
    name_map = {
        "arma_roller_FCR_E5e5_4coreDeskMinchen": "Armadillo-Roller",
        "cloth-ball": "Cloth-Ball",
        "cloth-funnel": "Cloth-Funnel",
        "n-body-simulation": "N-Bodies",
        "rodTwist_AWS": "Rod-Twist",
    }

    parser = argparse.ArgumentParser()
    parser.add_argument("-i,--input", dest="input", nargs="+", type=pathlib.Path)
    args = parser.parse_args()

    valid = True
    diffs = []

    npz_path = pathlib.Path(f"{args.input[0].parents[1].name}.npz")
    if npz_path.exists():
        diffs = numpy.load(npz_path)["arr_0"]
    else:
        for file in tqdm(args.input):
            with open(file) as f:
                data = json.load(f)
            valid = valid and all([v["valid"] for k, v in data.items()])
            diffs += [v["diff"] for k, v in data.items()]
        diffs = numpy.array(diffs)
        numpy.savez(npz_path, diffs)

    # print("{}: valid={} min_diff={:g} max_diff={:g} avg_diff={:g} stddev_diff={:g} median_diff={:g}".format(
    #     args.input[0].parents[1].name, valid, diffs.min(), diffs.max(), diffs.mean(), diffs.std(), numpy.median(diffs)))

    diffs = [numpy.load(p)["arr_0"] for p in pathlib.Path(".").glob("*.npz")]
    # diffs = [numpy.concatenate(diffs)]

    names = [name_map[p.stem] for p in pathlib.Path(".").glob("*.npz")]
    # names = [""]

    fig = plot_bar_with_outliers(diffs, names)
    fig.write_image("toi_compare.pdf")

if __name__ == "__main__":
    main()

