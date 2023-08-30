from flask import Flask, send_file, jsonify, request
from appium import webdriver
import io
import re
import xml.etree.ElementTree as ET
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

driver = None  # Global variable to store the Appium session

desired_caps = {
    'platformName': 'Android',
    'deviceName': 'AVYYUT1708002110'
}

def init_driver():
    global driver
    if driver is None:
        driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)


def get_screenshot():
    try:
        init_driver()
        screenshot = driver.get_screenshot_as_png()
        return screenshot
    except Exception as e:
        print(f"Error getting screenshot: {e}")
        return None


def get_domtree():
    try:
        init_driver()
        domtree = driver.page_source
        print("domtree:", domtree)
        return domtree
    except Exception as e:
        print(f"Error getting DOM tree: {e}")
        return None


def find_element_by_point(domtree, point):
    root = ET.fromstring(domtree)
    element = None
    print("point:", point)
    def dfs(current):
        nonlocal element
        for child in current:
            child_bounds = child.attrib.get('bounds')
            # 打印元素的矩形坐标
            # print("Element Bounds:", child_bounds)
            if child_bounds is not None and is_point_in_bounds(point, child_bounds):
                if element is None or get_area(child_bounds) < get_area(element.attrib['bounds']):
                    element = child
                    print("element:", element)
            dfs(child)

    def get_area(bounds):
        x1, y1, x2, y2 = map(int, re.findall(r'\d+', bounds))
        return (x2 - x1) * (y2 - y1)

    def is_point_in_bounds(point, bounds):
        x, y = map(int, re.findall(r'\d+', point))
        x1, y1, x2, y2 = map(int, re.findall(r'\d+', bounds))
        return x1 <= x <= x2 and y1 <= y <= y2

    dfs(root)
    # print(domtree)
    # element = root[0][0][0][0][0][0][0][0][0].attrib.get('bounds')
    return element




@app.route('/screenshot.png', methods=['GET'])
def get_screenshot_file():
    screenshot = get_screenshot()
    if screenshot is not None:
        return send_file(io.BytesIO(screenshot), mimetype='image/png')
    else:
        return "Error getting screenshot", 500


@app.route('/domtree', methods=['GET'])
def domtree():
    domtree = get_domtree()
    if domtree is not None:
        return jsonify(domtree)
    else:
        return "Error getting DOM tree", 500


@app.route('/highlight', methods=['POST'])
def highlight_element():
    try:
        # check if x and y parameters are in the request
        if 'x' not in request.form or 'y' not in request.form:
            return jsonify({'error': 'Missing x or y parameter'}), 400

        x = int(request.form.get('x'))
        y = int(request.form.get('y'))

        init_driver()
        # screenshot = driver.get_screenshot_as_png()
        domtree = driver.page_source

        # check if domtree is not empty
        if not domtree:
            return jsonify({'error': 'Empty domtree'}), 500

        element = find_element_by_point(domtree, f'[{x},{y}]')

        # print("x:", x, "y:", y)
        # print("element:", element)

        # check if element is not None
        if element is None:
            return jsonify({'error': 'No element found'}), 404

        # bounds = element.attrib.get('bounds')
        left, top, right, bottom =  map(int, re.findall (r'\d+', element.attrib['bounds']))

        highlighted_element = {
            'left': left,
            'top': top,
            'width': right - left,
            'height': bottom - top
        }
        print("highlighted_element:", highlighted_element)

        return highlighted_element

    except Exception as e:
        print(f"Error highlighting element: {e}")
        return jsonify({'error': f'Error highlighting element: {e}'}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
