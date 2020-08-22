from django.db import models
from django.conf import settings
from tag.models import Tag


class Node(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"<Node {self.id}: {self.name}>"


class SkillTree(models.Model):
    is_under_changing   = models.BooleanField(default=False)
    last_modified       = models.DateTimeField(auto_now=True)
    root_node           = models.OneToOneField(Node, on_delete=models.CASCADE)

    def __str__(self):
        return f"<SkillTree {self.id}: {self.name}>"

    @property
    def name(self):
        return self.root_node.name


class NodeToNode(models.Model):
    parent          = models.ForeignKey(Node, 
                        on_delete=models.CASCADE,
                        related_name="ntn_parent_records")

    child           = models.ForeignKey(Node, 
                        on_delete=models.CASCADE,
                        related_name="ntn_child_records")

    beloging_tree   = models.ForeignKey(SkillTree, 
                        on_delete=models.CASCADE,
                        related_name="ntn_beloging_tree_records")


class LightNode(models.Model):
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class ModifyRequest(models.Model):
    modify_reason    = models.TextField()
    commit_datetime  = models.DateTimeField(auto_now_add=True)
    new_tree_root    = models.OneToOneField(Node, on_delete=models.CASCADE)
    target_tree      = models.OneToOneField(SkillTree, on_delete=models.CASCADE)
    owner            = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)