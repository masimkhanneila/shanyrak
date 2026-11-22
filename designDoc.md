# Design Doc for Saniraq.kz
## 1) What should saniraq.kz do?
 - registration using jwt 
 - login 
 - changing user's data 
 - get user's data
 - creating apartment listing 
 - get/edit/delete listing 
 - adding/get list of/edit/delete comments to the listing 

## 2) Entities :
 - User
 - Apartment
 - Comments to the listing

## 3) Entity properties :
### User:
1) name 
2) phone number
3) password

### Apartment :
1) id
2) user_id
3) address
4) area

### Comment :
1) id
2) author_id
3) apartment_id
4) text
5) date

## 4) System Behavior
1) register/create user
2) login user
3) update/edit user
4) get user's data 
5) create apartment listing 
6) get listing 
7) update/edit listing 
8) delete listing 
9) adding comments to the lsiting 
10) get list of comments
11) get the number of comments
12) edit comments
13) delete comments

## 5) API Endpoints
### User:
1) POST/user
2) POST /auth/login
3) GET/user/{id}
4) PATCH/user/{id}

### Apartment :
1) POST/apartment
2) GET/apartment/{id}
3) PATCH/apartment/{id}
4) DELETE/apartment/{id}

### Comments to the listing:
1) POST/comment
2) GET/comments
3) GET/comments.size
4) PATCH/comment/{id}
5) DELETE/comment/{id}

## 6) Database 
Table : User 

| Type    | Column       |
|---------|--------------|
| PK      | id           |
| VARCHAR | name         |
| VARCHAR | phone_number |
| VARCHAR | password     |

Table : Apartment

| Type    | Column  |
|---------|---------|
| PK      | id      |
| FK      | user_id |
| VARCHAR | address |
| INT     | area    |

Table : Comment

| Type     | Column    |
|----------|-----------|
| PK       | id        |
| FK       | author_id |
| FK       | user_id   |
| VARCHAR  | text      |
| DATETIME | date      |

## 7) Relationships between entities:
One user can have several aprtment but apartment belongs to only one user.<br>
User 1 : N apartment<br>
Many apartments can have many comments but one comment belongs to only one apartment.<br>
Apartment 1 : N comment<br>
One user can have many comments,many user may have many comments<br>
User 1 : N comment

## 8) Technologies :
FastAPI 
JWT 
OAuth2PasswordBearer
SQLite