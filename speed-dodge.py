from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math

# Camera-related variables
camera_pos = (0,500,300)
# camera_pos = (0, 290, 100)

fovY = 120  # Field of view
GRID_LENGTH = 600  # Length of grid lines
point = 0
road_line_y = [-400, 200] # (y) as x and z = 0 always 
car_pos = 1
lane = [400, 0, -400]
obstacle_y = -600
obstacle_x = 0
game_over = False
police_pos = 1
police_y = 750
obstacle_speed = 1
cheat_mode = False
hit = 0
fp_view = False
bullets = []
bullet_speed = 10
bullet_hit_count = 0


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, 1000, 0, 800)  # left, right, bottom, top

    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_road_surroundings():
    tree_shift = road_line_y[0]  
    tree_spacing = 300
    distance_from_road = 750  
    pole_offset = 800  
    bush_height = 20

    # Roadside Bushes
    glPushMatrix()
    glColor3f(0.0, 0.8, 0.0)
    glBegin(GL_QUADS)
    for x in [-distance_from_road, distance_from_road]:
        glVertex3f(x - 20, -600 + tree_shift, 0)
        glVertex3f(x + 20, -600 + tree_shift, 0)
        glVertex3f(x + 20, 800 + tree_shift, 0)
        glVertex3f(x - 20, 800 + tree_shift, 0)
    glEnd()
    glPopMatrix()

    # Roadside Trees
    for x in [-distance_from_road, distance_from_road]:
        for y in range(-600, 800, tree_spacing):
            # Trunk
            glPushMatrix()
            glColor3f(0.55, 0.27, 0.07)
            glTranslatef(x, y + tree_shift, 40)
            glScalef(20, 20, 120)
            glutSolidCube(1)
            glPopMatrix()

            # Leaves
            glPushMatrix()
            glColor3f(0.0, 0.6, 0.0)
            glTranslatef(x, y + tree_shift, 120)
            glScalef(60, 60, 60)
            glutSolidSphere(1, 10, 10)
            glPopMatrix()

    # Random Trash Bins
    # random.seed(0)
    for x in [-distance_from_road + 40, distance_from_road - 40]:
        for y in range(-500, 800, 600):
            glPushMatrix()
            glColor3f(0.4, 0.4, 0.4)
            glTranslatef(x, y + tree_shift, 15)
            glScalef(15, 15, 30)
            glutSolidCube(1)
            glPopMatrix()
    

    # Lampposts with lights
    lamp_positions = []
    for x in [-pole_offset, pole_offset]:
        for y in range(-600, 800, 400):
            y_shifted = y + tree_shift
            lamp_positions.append((x, y_shifted))

            # Pole
            glPushMatrix()
            glColor3f(0.7, 0.7, 0.7)
            glTranslatef(x, y_shifted, 60)
            glScalef(8, 8, 180)
            glutSolidCube(1)
            glPopMatrix()

            # Lamp Glow (Night Mode)
            glPushMatrix()
            glColor3f(1.0, 1.0, 0.5)
            glTranslatef(x, y_shifted, 130)
            glScalef(25, 25, 25)
            glutSolidCube(1)
            glPopMatrix()

    # Parabolic Electric Wires
    glColor3f(0.2, 0.4, 0.2) 
    for i in range(0, len(lamp_positions) - 2, 2):
        if lamp_positions[i][0] == lamp_positions[i + 2][0]:
            x = lamp_positions[i][0]
            y1 = lamp_positions[i][1]
            y2 = lamp_positions[i + 2][1]
            z_top = 130

            glBegin(GL_LINE_STRIP)
            for t in range(0, 101):
                t_norm = t / 100
                y = y1 + (y2 - y1) * t_norm
                z = z_top - 20 * math.sin(math.pi * t_norm) #center point
                glVertex3f(x, y, z)
            glEnd()
def move_and_draw_bullets():
    global bullets, obstacle_x, obstacle_y, bullet_hit_count

    new_bullets = []
    for bullet in bullets:
        bullet['y'] -= bullet_speed
        
        # Draw bullet
        glPushMatrix()
        glColor3f(1, 1, 1)
        glTranslatef(bullet['x'], bullet['y'], bullet['z'])
        glutSolidSphere(10, 10, 10)
        glPopMatrix()

        # Check for collision
        if abs(bullet['x'] - obstacle_x) < 50 and abs(bullet['y'] - obstacle_y) < 50:
            bullet_hit_count += 1
            if bullet_hit_count == 3:
                obstacle_y = -600
                obstacle_x = random.choice([400, 0, -400])
                bullet_hit_count = 0
            continue 
        
       # Only keep bullets that are still on screen
        if bullet['y'] > -600:
            new_bullets.append(bullet)
            
    bullets = new_bullets
def draw_player_car(x, y, z=0):
    # Body
    glPushMatrix()
    glColor3f(1, 1, 0)  # Yellow
    glTranslatef(x, y, z + 15)
    glScalef(100, 200, 30)
    glutSolidCube(1)
    glPopMatrix()

    # Windshield
    glPushMatrix()
    glColor3f(0.1, 0.1, 0.1)
    glTranslatef(x, y, z + 35)
    glScalef(60, 100, 10)
    glutSolidCube(1)
    glPopMatrix()

    # Wheels
    for dx in [-30, 30]:
        for dy in [-60, 60]:
            glPushMatrix()
            glColor3f(0, 0, 0)
            glTranslatef(x + dx, y + dy, z + 5)
            glutSolidTorus(2, 10, 8, 8)
            glPopMatrix()
            
def draw_police_car(x, y, z=0):
    # Body
    glPushMatrix()
    glColor3f(1, 0, 0)  # Red
    glTranslatef(x, y, z + 15)
    glScalef(100, 200, 30)
    glutSolidCube(1)
    glPopMatrix()

    # Roof lights
    glPushMatrix()
    glColor3f(0, 0, 1)  # Blue light
    glTranslatef(x - 20, y, z + 40)
    glScalef(10, 30, 10)
    glutSolidCube(1)
    glPopMatrix()

    glPushMatrix()
    glColor3f(1, 1, 1)  # White light
    glTranslatef(x + 20, y, z + 40)
    glScalef(10, 30, 10)
    glutSolidCube(1)
    glPopMatrix()

def draw_obstacle_car(x, y, z=0):
    glPushMatrix()
    glColor3f(0, 1, 1)  # Cyan
    glTranslatef(x, y, z + 15)
    glScalef(100, 200, 30)
    glutSolidCube(1)
    glPopMatrix()

def keyboardListener(key, x, y):
    global cheat_mode, fp_view, camera_pos, point, road_line_y, car_pos, lane, obstacle_x, obstacle_y, police_pos, hit, obstacle_speed, police_y, game_over
    if(key == b"c"):
        cheat_mode = not cheat_mode
    if(key == b"f"):
        fp_view = not fp_view
    if(key == b"r" and game_over):
        camera_pos = (0,500,300)
        point = 0
        road_line_y = [-400, 200] # (y) as x and z = 0 always 
        car_pos = 1
        lane = [400, 0, -400]
        obstacle_y = -600
        obstacle_x = 0
        game_over = False
        police_pos = 1
        police_y = 750
        obstacle_speed = 1
        cheat_mode = False
        hit = 0
        fp_view = False
        bullets.clear()
    elif key == b' ':
        car_x = lane[car_pos]
        bullets.append({'x': car_x, 'y': 300, 'z': 15})

def specialKeyListener(key, x, y):
    if(game_over): return
    global car_pos
    if(key == GLUT_KEY_RIGHT):
        if(car_pos != 2):
            car_pos += 1
    if(key == GLUT_KEY_LEFT):
        if(car_pos != 0):
            car_pos -= 1
            

        


def setupCamera():
    glMatrixMode(GL_PROJECTION)  # Switch to projection matrix mode
    glLoadIdentity()  # Reset the projection matrix
    # Set up a perspective projection (field of view, aspect ratio, near clip, far clip)
    gluPerspective(fovY, 1.25, 0.1, 1500) # Think why aspect ration is 1.25?
    glMatrixMode(GL_MODELVIEW)  # Switch to model-view matrix mode
    glLoadIdentity()  # Reset the model-view matrix

    # Extract camera position and look-at target
    x, y, z = camera_pos
    # Position the camera and set its orientation
    if(fp_view):
        gluLookAt(x, y, z,  # Camera position
              lane[car_pos], 0, 0,  # Look-at target
              0, 0, 1)  # Up vector (z-axis)
    else:
        gluLookAt(x, y, z,  # Camera position
              0, 0, 0,  # Look-at target
              0, 0, 1)  # Up vector (z-axis)


def idle():
    glutPostRedisplay()

def change_line_y():
    if(game_over): return
    global road_line_y
    for i in range(len(road_line_y)):
        road_line_y[i] += obstacle_speed
        if(road_line_y[i] >= 600):
            road_line_y[i] = -600
def road_line():
    glPushMatrix()
    glColor3f(1, 1, 1)
    glTranslatef(0, road_line_y[0], 0)
    glScalef(30, 100, 2)
    glutSolidCube(1)
    glPopMatrix()

    glPushMatrix()
    glColor3f(1, 1, 1)
    glTranslatef(0, road_line_y[1], 0)
    glScalef(30, 100, 2)
    glutSolidCube(1)
    glPopMatrix()

def car_show():
    # Player car (detailed sports car appearance)
    glPushMatrix()
    glTranslatef(lane[car_pos], 300, 0)
    
# Wheels
    for x_offset in [-60, 60]:
        for z_offset in [-25, 25]:
            glPushMatrix()
            glColor3f(0.1, 0.1, 0.1)  # Black tires
            glTranslatef(x_offset, 0, z_offset)
            glRotatef(90, 0, 1, 0)
            glutSolidTorus(10, 15, 10, 10)
            glPopMatrix()
    
    # Main body
    glPushMatrix()
    glColor3f(0, 0.5, 1)  # Bright blue
    glScalef(80, 160, 40)
    glutSolidCube(1)
    glPopMatrix()
    
    # Windshield
    glPushMatrix()
    glColor3f(0.7, 0.9, 1)  # Light blue glass
    glTranslatef(0, 40, 30)
    glScalef(70, 60, 5)
    glutSolidCube(1)
    glPopMatrix()
    glPopMatrix()

def random_obstacle():
    glPushMatrix()
    glColor3f(0, 1, 1)
    glTranslatef(obstacle_x, obstacle_y, 0)
    glutSolidCube(100)
    glPopMatrix()

def move_obstacle():
    global obstacle_y, obstacle_x, point, game_over, hit, police_y, obstacle_speed, car_pos
    if(game_over): return
    if(obstacle_y >= 600):
        obstacle_x = random.choice([400, 0, -400])
        obstacle_y = -600
        point += 1
        if(point <= 220):
            obstacle_speed += 0.075
    else:
        obstacle_y += obstacle_speed
    
    if(obstacle_x == lane[car_pos] and 120 <= obstacle_y <= 250 ):
        obstacle_x = random.choice([400, 0, -400])
        obstacle_y = -600
        hit += 1
        if(hit == 1):
            police_y = 550
        elif(hit == 2):
            game_over = True 
    
    if(cheat_mode and 100 <= obstacle_y <= 119 and obstacle_x == lane[car_pos]):
        if(car_pos == 2):
            car_pos -= 1
        elif(car_pos == 1):
            car_pos += random.choice([1, -1])
        else: 
            car_pos += 1
        obstacle_y = 120
        

def police_show():
    # Police car (realistic design)
    glPushMatrix()
    glTranslatef(lane[police_pos], police_y, 0)
    
   # Wheels
    for x_offset in [-60, 60]:
        for z_offset in [-25, 25]:
            glPushMatrix()
            glColor3f(0.2, 0.4, 0.2)  # Black tires
            glTranslatef(x_offset, 0, z_offset)
            glRotatef(90, 0, 1, 0)
            glutSolidTorus(10, 15, 10, 10)
            glPopMatrix()
    
    
    # Main body
    glPushMatrix()
    glColor3f(0.9, 0.9, 0.9)  # White base
    glScalef(80, 160, 40)
    glutSolidCube(1)
    glPopMatrix()
    
    # Police stripe
    glPushMatrix()
    glColor3f(0, 0, 0.8)  # Blue stripe
    glTranslatef(0, 0, 25)
    glScalef(85, 30, 5)
    glutSolidCube(1)
    glPopMatrix()
    
    # Light bar
    glPushMatrix()
    glColor3f(0.8, 0, 0)  # Red lights
    glTranslatef(0, 80, 35)
    glScalef(60, 10, 10)
    glutSolidCube(1)
    glPopMatrix()
    glPopMatrix()

def police_show():
    glPushMatrix()
    glColor3f(1, 0, 0)
    glTranslatef(lane[car_pos], police_y, 0)
    glScalef(100, 200, 20)
    glutSolidCube(1)
    glPopMatrix()
def showScreen():
    """
    Display function to render the game scene:
    - Clears the screen and sets up the camera.
    - Draws everything of the screen
    """
    # Clear color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()  # Reset modelview matrix
    glViewport(0, 0, 1000, 800)  # Set viewport size

    setupCamera()  # Configure camera perspective

    # Draw the grid (game floor)
    glBegin(GL_QUADS)
    
    glColor3f(0.48, 0.46, 0.46)
    glVertex3f(600, -600, 0)
    glVertex3f(-600, -600, 0)
    glVertex3f(-600, +600, 0)
    glVertex3f(600, 600, 0)
    glEnd()

    # road line 
    change_line_y()
    road_line()

    random_obstacle()
    move_obstacle()
    car_show()

    police_show()


    # Display game info text at a fixed screen position
    draw_text(10, 770, f"Total Point: {point}")
    if(cheat_mode):
        draw_text(10, 750, "Cheat Mode Activated")
    else:
        draw_text(10, 750, "Cheat Mode is not Activated")

    if(hit == 1):
        draw_text(760, 750, "Police is chasing")
    elif(hit == 2):
        draw_text(700, 750, "Game Over! Press 'R' to restart")

    draw_road_surroundings()
    move_and_draw_bullets()
    # Swap buffers for smooth rendering (double buffering)
    glutSwapBuffers()

def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, w / float(h or 1), 1.0, 100.0)
    glMatrixMode(GL_MODELVIEW)
    
# Main function to set up OpenGL window and loop
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Double buffering, RGB color, depth test
    glutInitWindowSize(1000, 800)  # Window size
    glutInitWindowPosition(0, 0)  # Window position
    wind = glutCreateWindow(b"3D OpenGL Intro")  # Create the window

    glutDisplayFunc(showScreen)  # Register display function
    glutKeyboardFunc(keyboardListener)  # Register keyboard listener
    glutSpecialFunc(specialKeyListener)
    glutIdleFunc(idle) # Register the idle function to move the bullet automatically
    glutReshapeFunc(reshape)
    glutMainLoop()  # Enter the GLUT main loop

if __name__ == "__main__":
    main()
