from gym_duckietown.tasks.task_solution import TaskSolution
import numpy as np
import cv2


class DontCrushDuckieTaskSolution(TaskSolution):
    def __init__(self, generated_task):
        super().__init__(generated_task)
        self.strip = 'right'
        self.angle = 35

    def env(self):
        return self.generated_task['env']

    def direction(self):
        return 1 if self.strip == 'right' else -1

    def changeStrip(self):
        count = 20
        env = self.env()
        direction = self.direction()
        img, _, _, _ = env.step([1, direction * self.angle/2])
        for i in range(count):
            img, _, _, _ = env.step([1, 0])
            env.render()
        img, _, _, _ = env.step([1, -direction * self.angle])
        self.strip = 'left' if self.strip == 'right' else 'right'

    def isClear(self, angle):
        env = self.env()
        if not angle:
            angle = self.angle
        direction = self.direction()
        img, _, _, _ = env.step([0, direction * angle])
        rotateContour = self.searchContour(env, img)
        img, _, _, _ = env.step([0, -direction * angle])
        return bool(rotateContour)

    def searchContour(self, env, img):
        img = cv2.cvtColor(np.ascontiguousarray(img), cv2.COLOR_BGR2RGB)
        mask = cv2.inRange(img, (0, 130, 170), (2, 250, 255))
        contour, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contour

    def solve(self):
        env = self.env()
        # getting the initial picture
        img, _, _, _ = env.step([0,0])
        
        condition = True
        while condition:
            img, reward, done, info = env.step([1, 0])
            contour = self.searchContour(env, img)
            if contour:
                _, _, _, h = cv2.boundingRect(contour[0])
                if h > 60 and self.isClear():
                    self.changeStrip()
            elif self.strip == 'left' and self.isClear(50):
                self.changeStrip()
            env.render()
