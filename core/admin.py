from django.contrib import admin

from .models import (
    Category,
    Tag,
    Blog,
    NewsArticle,
    Comment,
    Review,
    TeacherProfile,
    CommunityForum,
    ForumComment, Facility,
    Media,Application
)



# Admin for Category
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


admin.site.register(Category, CategoryAdmin)


# Admin for Tag
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']


admin.site.register(Tag, TagAdmin)


# Admin for Blog
class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at', 'updated_at']
    search_fields = ['title', 'content', 'author__email']
    list_filter = ['author', 'created_at', 'category']
    ordering = ['-created_at']


admin.site.register(Blog, BlogAdmin)


# Admin for NewsArticle
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'published_date', 'is_published']
    search_fields = ['title', 'content', 'author__email']
    list_filter = ['author', 'is_published', 'published_date', 'category']
    ordering = ['-published_date']


admin.site.register(NewsArticle, NewsArticleAdmin)


# Admin for Comment
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_object', 'created_at']
    search_fields = ['user__email', 'content']
    list_filter = ['created_at']
    raw_id_fields = ['user']


admin.site.register(Comment, CommentAdmin)


# Admin for Review
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'teacher', 'rating', 'created_at']
    search_fields = ['user__email', 'teacher__user__email', 'content']
    list_filter = ['teacher', 'rating', 'created_at']
    raw_id_fields = ['user', 'teacher']


admin.site.register(Review, ReviewAdmin)


# Admin for TeacherProfile
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio']
    search_fields = ['user__email', 'bio']
    raw_id_fields = ['user']


admin.site.register(TeacherProfile, TeacherProfileAdmin)


# Admin for CommunityForum
class CommunityForumAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'created_at', 'updated_at']
    search_fields = ['title', 'content', 'teacher__email']
    list_filter = ['teacher', 'created_at']
    ordering = ['-created_at']


admin.site.register(CommunityForum, CommunityForumAdmin)


# Admin for ForumComment
class ForumCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'forum', 'created_at']
    search_fields = ['user__email', 'forum__title', 'content']
    list_filter = ['forum', 'created_at']
    raw_id_fields = ['user', 'forum']


admin.site.register(ForumComment, ForumCommentAdmin)


class FacilityAdmin(admin.ModelAdmin):
    list_display = ['school', 'facility_type', 'name']
    search_fields = ['name', 'description']
    list_filter = ['facility_type', 'name']


admin.site.register(Facility, FacilityAdmin)


class MediaAdmin(admin.ModelAdmin):
    list_display = ['title', 'media_type']
    search_fields = ['title', 'media_type']
    list_filter = ['title', 'media_type']



admin.site.register(Media, MediaAdmin)



class ApplicationAdmin(admin.ModelAdmin):
    pass




admin.site.register(Application, ApplicationAdmin)

