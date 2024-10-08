from typing import Union


class Author:
    def __init__(self, name: str) -> None:
        self.name = name
        self.blogs = []
    
    def add_blog(self, blog):
        self.blogs.append(blog)



class Post:
    def __init__(self, authors, tags, categories) -> None:
        self.authors = authors
        self.categories = Category(categories)
    

class Comment:
    pass


class Category:
    pass


class Tag:
    pass


class Blog:
    def __init__(self, names: Union[list, str], author: Author, categories: list, posts: list) -> None:
        if type(names) is list:
            return [Blog(i, author, categories, posts) for i in names]
        self.author = author
        self.author.add_blog(self)
        self.categories = Category(categories)
        self.posts = Post(posts)
        self.name = names
    
    def __new__(self, names: Union[list, str], author: Author, categories: list, posts: list):
        if type(names) is list:
            return [Blog(i, author, categories, posts) for i in names]
        self.author = author
        self.author.add_blog(self)
        self.categories = Category(categories)
        self.posts = Post(posts)
        self.name = names
        return self
    

    def add_post(self, post: Post):
        self.posts.append(post)
    
    def add_category(self, category: Category):
        self.categories.append(category)


if __name__ == '__main__':
    a = Author('Legendalf')
    b = Blog(['food', 'Python'], a, ['a'], ['a'])