import matplotlib.pyplot as plt


def plot_xy(xy, fmt='', show=True):
    xs = [p[0] for p in xy]
    ys = [p[1] for p in xy]
    plt.plot(xs, ys)
    if show:
        plt.show()


def plot_xy_dict(d, fmt=''):
    for _, xy in d.items():
        plot_xy(xy, fmt=fmt, show=False)
    plt.show()

