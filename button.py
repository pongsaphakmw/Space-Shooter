import pygame
class Button:
    def __init__(self, image, pos, text, font, base_color, hover_color):
        self.image = image
        self.pos = pos
        self.text_input = text
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(topleft = self.pos)
        self.text_rect = self.text.get_rect(center = self.rect.center)
        self.text_rect.center = self.rect.center

    def update(self, surface):
        if self.image is not None:
            surface.blit(self.image, self.rect)
        surface.blit(self.text, self.text_rect)

    def check_input(self, pos):
        if self.rect.collidepoint(pos):
            return True
        else:
            return False

    def check_hover(self, pos):
        if self.rect.collidepoint(pos):
            self.text = self.font.render(self.text_input, True, self.hover_color)
            self.text_rect.center = self.rect.center
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)
            self.text_rect.center = self.rect.center
