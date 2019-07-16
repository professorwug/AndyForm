import cv2
import numpy as np
import sys
import os
from tkinter import messagebox
import matplotlib.pyplot as plt
import logging
import logging.handlers

filePath = "/Users/adjourner/Desktop/AndyForm Generation/"  # Where our file is located. Change this each time you move to a new computer.
minimumHorizontalLines = 5 # Set this to something around 2 less than the number of lines your petitions usually have.

logPath = filePath + "/Script/AndyNotes.log"
handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", logPath))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
root.addHandler(handler)


def main2(imgPath, count):
    # a second main function which shows images
    logging.info("Function Main 2 is up and running.")
    img = cv2.imread(imgPath)
    lines = lineMaker(img)
    xNotables, yNotables = notableWizard(lines, img)
    yMagic = 0
    sufficientLines = True
    plt.axis('off')
    try:
        yMagicNotables, yMagic = yWitch(yNotables)
        # We won't verify it if it works the first time - that would be too persnickety, and we'll assume people don't scan things upside down.
        # if len(yMagicNotables)>0:
        #     resized = cv2.resize(img, (int(img.shape[1] * 20 / 100),int(img.shape[0] * 20 / 100)), interpolation = cv2.INTER_AREA)
        #     cv2.imshow("Is this oriented correctly? Press 'y' or 'n'.",
        #                resized)
        #     key = cv2.waitKey(0) & 0xFF
        #     cv2.destroyAllWindows()
        #     if key != ord('y'):
        #         sufficientLines = False
        #     else:
        #         sufficientLines = True
    except Exception:
        sufficientLines = False
    if not sufficientLines or len(yMagicNotables) < minimumHorizontalLines:
        # if we don't find as many lines as we expect, we'll rotate the image
        # but we'll ask for user confirmation, just in case we rotate it incorrectly
        img2 = rotateImg(img, 90) # first rotation
        lines2 = lineMaker(img2)
        xNotables, yNotables = notableWizard(lines2, img2)
        sufficientLines = True
        try:
            yMagicNotables, yMagic = yWitch(yNotables)
            if len(yMagicNotables) > 0:
                resized = cv2.resize(img2, (int(img2.shape[1] * 40 / 100), int(img2.shape[0] * 40 / 100)),
                                     interpolation=cv2.INTER_AREA)
                logging.info("the image shape is "+ str(int(img2.shape[1] * 40 / 100)))
                cv2.imshow(
                    "We had to rotate Page " + str(count) +". Does it look all right? Press Y if it does and N if it doesn't",
                    resized)
                key = cv2.waitKey(0) & 0xFF
                cv2.destroyAllWindows()
                if key != ord('y'):
                    sufficientLines = False
                else:
                    sufficientLines = True
        except Exception:
            sufficientLines = False
        if not sufficientLines or len(yMagicNotables) < minimumHorizontalLines:
            sufficientLines = True
            img3 = rotateImg(img2, 90)  # second rotation
            lines3 = lineMaker(img3)
            xNotables, yNotables = notableWizard(lines3, img3)
            try:
                yMagicNotables, yMagic = yWitch(yNotables)
                if len(yMagicNotables) > 0:
                    resized = cv2.resize(img3, (int(img3.shape[1] * 40 / 100), int(img3.shape[0] * 40 / 100)),
                                         interpolation=cv2.INTER_AREA)
                    logging.info("the image shape is " + str(int(img3.shape[1] * 40 / 100)))
                    cv2.imshow(
                        "We had to rotate Page " + str(count) + ". Does it look all right? Press Y if it does and N if it doesn't",
                        resized)
                    key = cv2.waitKey(0) & 0xFF
                    cv2.destroyAllWindows()
                    if key != ord('y'):
                        sufficientLines = False
                    else:
                        sufficientLines = True
            except Exception:
                sufficientLines = False
            if not sufficientLines or len(yMagicNotables) < minimumHorizontalLines:
                sufficientLines = True
                img4 = rotateImg(img3, 90)  # third rotation
                lines4 = lineMaker(img4)
                xNotables, yNotables = notableWizard(lines4, img4)
                try:
                    yMagicNotables, yMagic = yWitch(yNotables)
                    if len(yMagicNotables) > 0:
                        resized = cv2.resize(img4, (int(img4.shape[1] * 40 / 100), int(img4.shape[0] * 40 / 100)),
                                             interpolation=cv2.INTER_AREA)
                        logging.info("the image shape is " + str(int(img4.shape[1] * 40 / 100)))
                        cv2.imshow(
                            "We had to rotate Page " + str(count) +". Does it look all right? Press Y if it does and N if it doesn't",
                            resized)
                        key = cv2.waitKey(0) & 0xFF
                        cv2.destroyAllWindows()
                        if key != ord('y'):
                            sufficientLines = False
                        else:
                            sufficientLines = True

                except Exception:
                    sufficientLines = False
                if not sufficientLines or len(yMagicNotables) < minimumHorizontalLines:
                    # all rotations have been tried. It's a lost case!
                    logging.info("We fail to read the image with yMagicNotables=" + str(yMagicNotables) + "and sufficientLines = " +str(sufficientLines))

                    resized = cv2.resize(img4, (int(img4.shape[1] * 40 / 100), int(img4.shape[0] * 40 / 100)),
                                     interpolation=cv2.INTER_AREA)
                    cv2.imshow("Error on Page" + str(count)+ "! Andy apologizes... He can't read this page. Maybe try rescanning it? (Press any key to continue)",resized)
                    key = cv2.waitKey(0) & 0xFF
                    # messagebox.showerror("AndyForm doesn't like this image...", "Error in Page " + str(count) + ". We didn't find enough lines. This may be due to poor image quality, or a skewed angle. You might try rescanning the sheets...")
                else:
                    cropMaker(xNotables, yMagicNotables, img4, count, yMagic)
            else:
                cropMaker(xNotables, yMagicNotables, img3, count, yMagic)
        else:
            cropMaker(xNotables, yMagicNotables, img2, count, yMagic)
    else:
        cropMaker(xNotables, yMagicNotables, img, count, yMagic)


def main(imgPath, count):
    img = cv2.imread(imgPath)
    lines = lineMaker(img)
    xNotables, yNotables = notableWizard(lines, img)
    sufficientLines = True
    try:
        yMagicNotables = yWitch(yNotables)
    except IndexError:
        sufficientLines = False
    if not sufficientLines or len(yMagicNotables) < minimumHorizontalLines:
        # if we don't find as many lines as we expect, we'll rotate the image
        img = rotateImg(img, 270)
        # cv2.imshow("rotated 90 degrees", img)
        # cv2.waitKey(0)
        lines = lineMaker(img)
        xNotables, yNotables = notableWizard(lines, img)
        sufficientLines = True
        try:
            yMagicNotables = yWitch(yNotables)
        except IndexError:
            sufficientLines = False
        if not sufficientLines or len(yMagicNotables) < minimumHorizontalLines:
            sufficientLines = True
            img = rotateImg(img, 180)  # and one more time, just in case
            lines = lineMaker(img)
            xNotables, yNotables = notableWizard(lines, img)
            try:
                yMagicNotables = yWitch(yNotables)
            except IndexError:
                sufficientLines = False
            if not sufficientLines or len(yMagicNotables) < minimumHorizontalLines:
                messagebox.showerror("AndyForm doesn't like this image...",
                                     "We didn't find enough lines. This may be due to poor image quality, or a skewed angle. You might try rescanning the sheets...")
            else:
                cropMaker(xNotables, yMagicNotables, img, count)
        else:
            cropMaker(xNotables, yMagicNotables, img, count)
    else:
        cropMaker(xNotables, yMagicNotables, img, count)


def rotateImg(image, angle):
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)

    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY

    # perform the actual rotation and return the image
    return cv2.warpAffine(image, M, (nW, nH))


def lineMaker(img):
    lineDistance = 42
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 300, apertureSize=5)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=5)
    return lines


'''
def nearPoint(dot, species):
    """Args: dot = the point to be tested; species = 0 for x, 1 for y.
    This guy yells True if the coordinate entered is within an arbitrary number of pixels from one already known"""
    tolerance = 5
    for stranger in seenPoints:
        if abs(stranger[species] - dot) < tolerance:
            return True
    return False
'''


def notableWizard(lines, img):
    dimensions = img.shape
    print(dimensions)
    suggestedYThresh = int(dimensions[1] * 0.6 * 0.5)  # this works for our petition because it has about four columns

    xShrimpThreshold = 20  # any lines shorter than this will be banned.
    yShrimpThreshold = suggestedYThresh
    disTolerance = 10  # what's the error when seeing if a point has already been found, or is vertical?

    xNotables = []
    yNotables = []
    for bob in lines:
        if abs(bob[0][0] - bob[0][2]) < disTolerance:
            # we have a vertical line! Is it already in xNotables?
            bobFound = False
            for karen in xNotables:
                if abs(bob[0][0] - karen[0]) < disTolerance:
                    karen[1].append(bob[0][1])  # add the corresponding y values
                    karen[1].append(bob[0][3])
                    bobFound = True
                    break
            if not bobFound:
                # print("here's vertical line 1: ", bob[0])
                xNotables.append([bob[0][0], [bob[0][1], bob[0][3]]])
        if abs(bob[0][1] - bob[0][3]) < disTolerance:
            # we have a vertical line! Is it already in yNotables?
            bobFound = False
            for cheyenne in yNotables:
                if abs(bob[0][1] - cheyenne[0]) < disTolerance:
                    cheyenne[1].append(bob[0][0])  # add the corresponding x values
                    cheyenne[1].append(bob[0][2])
                    bobFound = True
                    break
            if not bobFound:
                # print("here's vertical line 1: ", bob[0])
                yNotables.append([bob[0][1], [bob[0][0], bob[0][2]]])

    # Now we can process these notables and determine which correspond to skimpy little lines.
    # (Note: if your form doesn't have lines in the middle of boxes, this part isn't strictly necessary
    # - though it won't hurt)

    xPoints = []
    yPoints = []

    print("the intermediate notables are")
    print("x:", xNotables)
    print("y:", yNotables)

    for dude in xNotables:
        dude[1].sort()
        print("x's ys, sorted", dude[1])
        print("our x gap is", abs(dude[1][0] - dude[1][-1]))
        if abs(dude[1][0] - dude[1][-1]) > xShrimpThreshold:
            print("a vertical line:", (dude[0], dude[1][0]), (dude[0], dude[1][-1]))
            # cv2.line(img, (dude[0], dude[1][0]), (dude[0], dude[1][-1]), (0, 255, 0), 2)
            print("X found line of sufficient size")
            xPoints.append(dude[0])
    for dudett in yNotables:
        dudett[1].sort()
        print("y's xs, sorted", dudett[1])
        print("our y gap is", abs(dudett[1][0] - dudett[1][-1]))
        if abs(dudett[1][0] - dudett[1][-1]) > yShrimpThreshold:
            print("a horizontal line:", (dudett[1][0], dudett[0]), (dudett[1][-1], dudett[0]))
            # cv2.line(img, (dudett[1][0], dudett[0]), (dudett[1][-1], dudett[0]), (0, 255, 0), 2)
            print("Y found line of sufficient size")
            yPoints.append(dudett[0])
    xPoints.sort()
    yPoints.sort()
    logging.info("the x and y points, as determined by the Notable Wizard")
    logging.info(str(xPoints))
    logging.info(str(yPoints))
    # cv2.imshow('with notables',img)
    # cv2.waitKey(0)

    return xPoints, yPoints


'''
def findNotables(lines):
    """Discovers horizontal and vertical lines (within tolerance)"""
    # Discover most common distance, within tolerance
    xdisTolerance = 10
    magicLines = []  # for lines that fit the tolerance (to, later, find the earliest occurrence)
    # For x distance, we must ensure that the lines used are vertical (the endpoints have almost the same x vals).
    xdistances = [0]
    xdisFreq = [0]
    xtol = 10
    ytol = 3
    xNotables = []
    yNotables = []
    for bob in lines:
        if abs(bob[0][0] - bob[0][2]) < xtol:
            # print("here's vertical line 1: ", bob[0])
            xNotables.append(bob[0][0])
        if abs(bob[0][1] - bob[0][3]) < ytol:
            # print("here's horizontal line 1: ", bob[0])
            yNotables.append(bob[0][1])
    xNotables.sort()
    # print(xNotables)
    i = 0
    xNotablesNew = []
    Ended = False
    while not Ended:
        a = 1
        while (xNotables[i + a] - xNotables[i + a - 1]) < 5:
            a += 1
            # print('incrementing')
            if a + i >= len(xNotables): break
        xNotablesNew.append(int(sum(xNotables[i:i + a]) / (a)))
        # print(xNotables[i:i+a], ' becomes', sum(xNotables[i:i+a])/(a))
        i += a
        # print('and i up')
        if i >= len(xNotables) - 1: Ended = True
    xNotables = xNotablesNew
    yNotables.sort()
    i = 0
    yNotablesNew = []
    Ended = False
    while not Ended:
        a = 1
        while (yNotables[i + a] - yNotables[i + a - 1]) < 5:
            a += 1
            # print('incrementing')
            if a + i >= len(yNotables): break
        yNotablesNew.append(int(sum(yNotables[i:i + a]) / (a)))
        # print(yNotables[i:i+a], ' becomes', sum(yNotables[i:i+a])/(a))
        i += a
        # print('and i up')
        if i >= len(yNotables) - 1: Ended = True
    yNotables = yNotablesNew
    print("XNotables: ", xNotables)
    print("YNotables: ", yNotables)
    return xNotables, yNotables
'''


def modeIt(yset):
    """Finds the mode of the distances between consecutive items in a sorted set"""
    # y magic coefficient - we can filter the mess of competing vertical lines by assuming that the wanted lines lie
    # a uniform distance from each other. Hence the y magic coefficient. It finds the most common gap between lines,
    # tests to see if its long enough, and rolls.
    gaps = []
    for i in range(len(yset) - 1):
        gaps.append(yset[i + 1] - yset[i])

    mode1 = max(gaps, key=gaps.count)
    print("Taking the mode! The most common is ", mode1)
    if mode1 > 50:  # Sometimes the text in the petition registers as a line, and produces a spurious most common gap.
        print("and that's big enough.")
        return mode1  # This will ensure that only large enough gaps get passed through.
    else:
        gaps2 = list(filter(lambda a: a != mode1, gaps))
        mode2 = max(gaps2, key=gaps2.count)
        print("Too small! Here' the second most common", mode2)
        return mode2


def yWitch(yNotables):
    yMagic = modeIt(yNotables)
    print('Dooba doo', yMagic)

    # filter yNotables for ymagic.
    witchesError = 10
    yMagicNotables = []

    for i in range(len(yNotables) - 1):
        # print('gap one forward', abs(abs(yNotables[i + 1] - yNotables[i]) - yMagic))
        # print('gap two forward', abs(abs(yNotables[i + 2] - yNotables[i + 1]) - yMagic))
        if i == 0:
            if abs(abs(yNotables[i + 1] - yNotables[i]) - yMagic) < witchesError and abs(
                    abs(yNotables[i + 2] - yNotables[i + 1]) - yMagic) < witchesError:
                yMagicNotables.append(yNotables[i])
        elif i >= len(yNotables) - 2:
            if abs(abs(yNotables[i - 1] - yNotables[i]) - yMagic) < witchesError and abs(
                    abs(yNotables[i - 2] - yNotables[i - 1]) - yMagic) < witchesError:
                yMagicNotables.append(yNotables[i])
        elif abs(abs(yNotables[i + 1] - yNotables[i]) - yMagic) < witchesError and abs(
                abs(yNotables[i + 2] - yNotables[i + 1]) - yMagic) < witchesError:
            yMagicNotables.append(yNotables[i])
        elif abs(abs(yNotables[i - 1] - yNotables[i]) - yMagic) < witchesError and abs(
                abs(yNotables[i - 2] - yNotables[i - 1]) - yMagic) < witchesError:
            yMagicNotables.append(yNotables[i])

    print("the sausage is made", yMagicNotables)
    return yMagicNotables, yMagic


"""
def yWitchOld(yNotables):
    yMagic = modeIt(yNotables)
    print('Dooba doo', yMagic)

    # filter yNotables for ymagic.
    witchesError = 5
    yMagicNotables = []

    # An alternate while-loop approach

    for i in range(len(yNotables) - 1):
        loopEntered = False
        days = i
        if abs(abs(yNotables[days + 1] - yNotables[days]) - yMagic) < witchesError or abs(
                abs(yNotables[days + 1] - yNotables[days]) - yMagic * 2) < witchesError:
            yMagicNotables.append(yNotables[days])
            days = i + 1
            while abs(abs(yNotables[days + 1] - yNotables[days]) - yMagic) < witchesError or abs(
                    abs(yNotables[days + 1] - yNotables[days]) - yMagic * 2) < witchesError:
                loopEntered = True
                yMagicNotables.append(yNotables[days])
                days += 1
                if days + 1 >= len(yNotables): break
            if len(yMagicNotables) > 3:
                yMagicNotables.append(yNotables[days])
                break
            else:
                yMagicNotables = []
    print(yMagicNotables)
    yMagicNotables = yMagicNotables[::2]  # Form dependent
    print("evened magic:", yMagicNotables)
    return yMagicNotables
"""


def cropMaker(xNotables, yMagicNotables, img, count,yMagic):
    for x1, x2 in zip(xNotables[:-1], xNotables[1:]):
        # print('xs come: ',x1,x2)
        for y1, y2 in zip(yMagicNotables[:-1], yMagicNotables[1:]):
            # print('ys come: ', y1, y2)
            area = (y2 - y1) * (x2 - x1)
            if abs(abs(y2 - y1) - yMagic) < 10 and (y2 - y1)*3 < (x2-x1):
                print('sufficient area')
                crop = img[y1:y2, x1:x2]
                yCoord = str(y1)
                if len(yCoord) < 4: yCoord = ''.join(["0" for i in range(4 - len(yCoord))]) + yCoord
                xCoord = str(x1)
                if len(xCoord) < 4: xCoord = ''.join(["0" for i in range(4 - len(xCoord))]) + xCoord
                cv2.imwrite(filePath + 'Crops/page' + str(count) + '-' + yCoord + '_' + xCoord + '.jpg', crop)


images = os.listdir(filePath + "Pages")
print('here are the images:', images)
count = 0
for imgPath in images:
    if imgPath[0] != '.':
        count += 1
        print("running with this file:", imgPath)
        main2(filePath + "Pages/" + imgPath, count)
