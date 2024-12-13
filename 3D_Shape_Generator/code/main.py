import cv2
import os
from solid import cube, cylinder, scad_render_to_file, polyhedron


# Function to detect shape
def detect_shape(view, view_name):
    if view is None:
        raise ValueError(f"{view_name} image could not be loaded. Check the file path.")

    gray_image = cv2.cvtColor(view, cv2.COLOR_BGR2GRAY)
    _, thresh_image = cv2.threshold(gray_image, 220, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for i, contour in enumerate(contours):
        if i == 0:
            continue  # Skip the outermost contour

        epsilon = 0.01 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        if len(approx) == 3:
            return "Triangle"
        elif len(approx) == 4:
            (x, y, w, h) = cv2.boundingRect(approx)
            aspect_ratio = w / float(h)
            if 0.95 <= aspect_ratio <= 1.05:
                return "Square"
            else:
                return "Rectangle"
        elif len(approx) == 5:
            return "Pentagon"
        elif len(approx) == 6:
            return "Hexagon"
        else:
            return "Circle"

    return "Unknown"


# Function to identify 3D shape
def identify_3d_shape(front_view, top_view, side_view):
    front_shape = detect_shape(front_view, "Front")
    top_shape = detect_shape(top_view, "Top")
    side_shape = detect_shape(side_view, "Side")

    if front_shape == "Square" and top_shape == "Square" and side_shape == "Square":
        return "Cube"
    elif front_shape == "Rectangle" and top_shape == "Circle" and side_shape == "Rectangle":
        return "Cylinder"
    elif front_shape == "Triangle" and top_shape == "Circle" and side_shape == "Triangle":
        return "Cone"
    elif front_shape == "Triangle" and top_shape == "Square" and side_shape == "Triangle":
        return "Pyramid"
    else:
        return "Shape not recognized"


# Function to create a 3D model
def create_3d_model(shape, dimensions, output_file):
    width, depth, height = dimensions
    if shape == "Cube":
        model = cube([width, depth, height])
    elif shape == "Cylinder":
        radius = width / 2.0
        model = cylinder(r=radius, h=height)
    elif shape == "Cone":
        radius = width / 2.0
        model = cylinder(r1=radius, r2=0, h=height)  # Cone: Circular base with apex
    elif shape == "Pyramid":
        model = polyhedron(
            points=[
                [0, 0, 0], [width, 0, 0], [width, depth, 0], [0, depth, 0],  # Base points
                [width / 2, depth / 2, height]  # Apex
            ],
            faces=[
                [0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4],  # Sides
                [0, 1, 2, 3]  # Base
            ]
        )
    else:
        raise ValueError(f"Unsupported shape: {shape}")

    scad_render_to_file(model, output_file)
    print(f"3D model for {shape} saved as '{output_file}'.")


# Main function
if __name__ == "__main__":
    # File paths for the views
    front_path = r"C:\Users\Akshay\Downloads\3D_Shape_Generator\3D_Shape_Generator\images\conefrontview.png"
    top_path = r"C:\Users\Akshay\Downloads\3D_Shape_Generator\3D_Shape_Generator\images\conetopview.png"
    side_path = r"C:\Users\Akshay\Downloads\3D_Shape_Generator\3D_Shape_Generator\images\conesideview.png"

    # Load images
    front_view = cv2.imread(front_path)
    top_view = cv2.imread(top_path)
    side_view = cv2.imread(side_path)

    # Check for valid images
    if front_view is None or top_view is None or side_view is None:
        raise FileNotFoundError("One or more view images could not be loaded. Please check the file paths.")

    # Identify the 3D shape
    shape = identify_3d_shape(front_view, top_view, side_view)
    print(f"Detected 3D shape: {shape}")

    # Example dimensions (replace with actual dimensions)
    dimensions = (50, 50, 100)  # Width, Depth, Height

    # Create output folder
    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)

    # Generate and save the SCAD file
    if shape != "Shape not recognized":
        output_file = os.path.join(output_folder, f"{shape.lower()}_model.scad")
        create_3d_model(shape, dimensions, output_file)
    else:
        print("Unable to generate 3D model. Shape could not be recognized.")
