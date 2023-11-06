from comments.models import Comment
from comments.serializers import CommentSerializer

class CommentDescSerializer(CommentSerializer):
    class Meta:
        model = Comment
        fields = ('commentID', 'content', 'author', 'post', 'created', 'last_modified', 'parent', 'reply_to',
                  'like_count', 'collect_count', 'reply_count')
        read_only_fields = ("__all__",)