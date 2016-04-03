import numpy as np
import matplotlib.pyplot as plt

"""
Plots line graph for a single countries attributes. Given a single x axis
and a list of ys in the form of (data, name)
"""
def plotCountry(x, xName, ys, title, decorations = 'k'):
    # Handlet the different possible inputs given to function
    if not isinstance(ys, list):
        ys = [ys]
    if not isinstance(decorations, list):
        decorations = [decorations for _ in range(len(ys))]
    if len(ys) != len(decorations):
        raise ValueError("Number of lines to plot does not equal the amount" \
                + " of decorations give.")

    # Plot all of the lines given
    for yindex, y in enumerate(ys):
        plt.plot(x, y[0], decorations[yindex], label=y[1])

    # Labelling0
    plt.xlabel(xName)
    if len(ys) == 1:
        plt.ylabel(ys[0][1])
    else:
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.title(title)

    plt.show()

def testPlotCountry():
    t = range(5)
    y1 = np.matrix([[1], [2], [3], [4], [5]])
    y2 = np.matrix([[5], [4], [3], [2], [1]])
    plotCountry(t, "Time", (y1, "Y1"), "Test1")
    plotCountry(t, "Time", [(y1, "Y1"), (y2, "Y2")], "Test 2",
            decorations=['bo', 'r^'])

if __name__ == '__main__':
    test()
