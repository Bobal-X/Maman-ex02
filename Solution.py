from typing import List, Tuple
from psycopg2 import sql
from datetime import date, datetime
import Utility.DBConnector as Connector
from Utility.ReturnValue import ReturnValue
from Utility.Exceptions import DatabaseException
from Business.Customer import Customer, BadCustomer
from Business.Order import Order, BadOrder
from Business.Dish import Dish, BadDish
from Business.OrderDish import OrderDish


# ---------------------------------- CRUD API: ----------------------------------
# Basic database functions


def create_tables() -> None:
    conn = None
    try:
        conn = Connector.DBConnector()
        conn.execute("""CREATE TABLE Customers(
                            cust_id INTEGER PRIMARY KEY CHECK (cust_id > 0),
                            full_name TEXT NOT NULL,
                            age INTEGER NOT NULL CHECK (age >= 18), CHECK (age <= 120),
                            phone TEXT NOT NULL CHECK ( LENGTH(phone) = 10 ));
                     """)
        conn.execute("""CREATE TABLE Orders(
                            order_id INTEGER PRIMARY KEY CHECK (order_id > 0),
                            date TIMESTAMP(0) NOT NULL,
                            delivery_fee DECIMAL NOT NULL CHECK (delivery_fee >= 0),
                            delivery_address TEXT NOT NULL CHECK ( LENGTH(delivery_address) >= 5 ));
                     """)
        conn.execute("""CREATE TABLE Dishes(
                            dish_id INTEGER PRIMARY KEY CHECK (dish_id > 0),
                            name TEXT NOT NULL CHECK ( LENGTH(name) >= 4 ),
                            price DECIMAL NOT NULL CHECK (price > 0),
                            is_active BOOLEAN NOT NULL);
                     """)
        conn.execute("""CREATE TABLE OrderCustomer(
                            order_id INTEGER PRIMARY KEY CHECK (order_id > 0),
                            cust_id INTEGER NOT NULL CHECK (cust_id > 0),
                            FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE,
                            FOREIGN KEY (cust_id) REFERENCES Customers(cust_id) ON DELETE CASCADE);
                     """)
        conn.execute("""CREATE TABLE OrderDish(
                            order_id INTEGER,
                            dish_id INTEGER NOT NULL,
                            current_price DECIMAL NOT NULL CHECK (current_price > 0),
                            amount INTEGER NOT NULL CHECK (amount >= 0),
                            FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE,
                            FOREIGN KEY (dish_id) REFERENCES Dishes(dish_id) ON DELETE CASCADE,
                            PRIMARY KEY (order_id, dish_id));
                     """)
        conn.execute("""CREATE TABLE Ratings(
                            cust_id INTEGER,
                            dish_id INTEGER NOT NULL,
                            rating INTEGER NOT NULL CHECK (rating >= 1) CHECK (rating <= 5),
                            FOREIGN KEY (cust_id) REFERENCES Customers(cust_id) ON DELETE CASCADE,
                            FOREIGN KEY (dish_id) REFERENCES Dishes(dish_id) ON DELETE CASCADE,
                            PRIMARY KEY (cust_id, dish_id));
                     """)
        conn.execute("""CREATE VIEW OrdersPrices AS SELECT O.order_id AS order_id, SUM(COALESCE(OD.current_price * OD.amount,0)) + O.delivery_fee AS subtotal
                                                    FROM Orders O  LEFT JOIN OrderDish OD on O.order_id = OD.order_id
                                                    GROUP BY O.order_id;
                     """)
    except DatabaseException.ConnectionInvalid as e:
        # do stuff
        print(e)
    except DatabaseException.NOT_NULL_VIOLATION as e:
        # do stuff
        print(e)
    except DatabaseException.CHECK_VIOLATION as e:
        # do stuff
        print(e)
    except DatabaseException.UNIQUE_VIOLATION as e:
        # do stuff
        print(e)
    except DatabaseException.FOREIGN_KEY_VIOLATION as e:
        # do stuff
        print(e)
    except Exception as e:
        print(e)
    finally:
        # will happen any way after code try termination or exception handling
        conn.close()


def clear_tables() -> None:
    conn = None
    try:
        conn = Connector.DBConnector()
        conn.execute("DELETE FROM Customers")
        conn.execute("DELETE FROM Orders")
        conn.execute("DELETE FROM Dishes")
        conn.execute("DELETE FROM OrderDish")
        conn.execute("DELETE FROM Ratings")
    except DatabaseException.ConnectionInvalid as e:
        # do stuff
        print(e)
    except DatabaseException.NOT_NULL_VIOLATION as e:
        # do stuff
        print(e)
    except DatabaseException.CHECK_VIOLATION as e:
        # do stuff
        print(e)
    except DatabaseException.UNIQUE_VIOLATION as e:
        # do stuff
        print(e)
    except DatabaseException.FOREIGN_KEY_VIOLATION as e:
        # do stuff
        print(e)
    except Exception as e:
        print(e)
    finally:
        conn.close()


def drop_tables() -> None:
    conn = None
    try:
        conn = Connector.DBConnector()
        conn.execute("DROP TABLE IF EXISTS Customers CASCADE")
        conn.execute("DROP TABLE IF EXISTS Orders CASCADE")
        conn.execute("DROP TABLE IF EXISTS Dishes CASCADE")
        conn.execute("DROP TABLE IF EXISTS OrderCustomer CASCADE")
        conn.execute("DROP TABLE IF EXISTS OrderDish CASCADE")
        conn.execute("DROP TABLE IF EXISTS Ratings CASCADE")
    except DatabaseException.ConnectionInvalid as e:
        # do stuff
        print(e)
    except DatabaseException.NOT_NULL_VIOLATION as e:
        # do stuff
        print(e)
    except DatabaseException.CHECK_VIOLATION as e:
        # do stuff
        print(e)
    except DatabaseException.UNIQUE_VIOLATION as e:
        # do stuff
        print(e)
    except DatabaseException.FOREIGN_KEY_VIOLATION as e:
        # do stuff
        print(e)
    except Exception as e:
        print(e)
    finally:
        conn.close()


# CRUD API

def add_customer(customer: Customer) -> ReturnValue:
    conn, final_status = None, ReturnValue.OK
    try:
        conn = Connector.DBConnector()
        query = sql.SQL("INSERT INTO Customers(cust_id, full_name, age, phone) Values({cust_id}, {full_name}, {age}, {phone})").format(cust_id=sql.Literal(customer.get_cust_id()),
                      full_name=sql.Literal(customer.get_full_name()),
                      age=sql.Literal(customer.get_age()),
                      phone=sql.Literal(customer.get_phone()))

        conn.execute(query)
    except DatabaseException.ConnectionInvalid as e:
        final_status = ReturnValue.ERROR
    except DatabaseException.NOT_NULL_VIOLATION as e:
        final_status = ReturnValue.BAD_PARAMS
    except DatabaseException.CHECK_VIOLATION as e:
        final_status = ReturnValue.BAD_PARAMS
    except DatabaseException.UNIQUE_VIOLATION as e:
        final_status = ReturnValue.ALREADY_EXISTS
    except DatabaseException.FOREIGN_KEY_VIOLATION as e:
        final_status = ReturnValue.BAD_PARAMS
    except Exception as e:
        final_status = ReturnValue.ERROR
    finally:
        conn.close()
        return final_status



def get_customer(customer_id: int) -> Customer:
    conn, results_count, result, failed = None, None, None, False
    try:
        conn = Connector.DBConnector()
        query = sql.SQL("SELECT * FROM Customers WHERE cust_id={cust_id}").format(cust_id=sql.Literal(customer_id))
        results_count, result = conn.execute(query)
    except Exception as e:
        failed = True
    finally:
        conn.close()
        if results_count != 1 or failed:
            return BadCustomer()
        else:
            return Customer(**result[0])



def delete_customer(customer_id: int) -> ReturnValue:
    conn, results_count, result, final_status = None, None, None, ReturnValue.OK
    try:
        conn = Connector.DBConnector()
        query = sql.SQL("DELETE FROM Customers WHERE cust_id={cust_id}").format(cust_id=sql.Literal(customer_id))
        results_count, _ = conn.execute(query)
    except Exception as e:
        final_status = ReturnValue.ERROR
    finally:
        conn.close()
        if results_count == 0:
            final_status = ReturnValue.NOT_EXISTS
        return final_status


def add_order(order: Order) -> ReturnValue:
    conn, final_status = None, ReturnValue.OK
    try:
        conn = Connector.DBConnector()
        query = (sql.SQL("INSERT INTO Orders(order_id, date, delivery_fee, delivery_address) "
                        "Values({order_id}, {order_date}, {delivery_fee}, {delivery_address})").format(
                            order_id=sql.Literal(order.get_order_id()),
                            order_date=sql.Literal(format_timestamp_for_sql(order.get_datetime())),
                            delivery_fee=sql.Literal(order.get_delivery_fee()),
                            delivery_address=sql.Literal(order.get_delivery_address())))

        conn.execute(query)
    except DatabaseException.ConnectionInvalid as e:
        final_status = ReturnValue.ERROR
    except DatabaseException.NOT_NULL_VIOLATION as e:
        final_status = ReturnValue.BAD_PARAMS
    except DatabaseException.CHECK_VIOLATION as e:
        final_status = ReturnValue.BAD_PARAMS
    except DatabaseException.UNIQUE_VIOLATION as e:
        final_status = ReturnValue.ALREADY_EXISTS
    except DatabaseException.FOREIGN_KEY_VIOLATION as e:
        final_status = ReturnValue.BAD_PARAMS
    except Exception as e:
        final_status = ReturnValue.ERROR
    finally:
        conn.close()
        return final_status


def get_order(order_id: int) -> Order:
    conn, results_count, result, failed = None, None, None, False
    try:
        conn = Connector.DBConnector()
        query = sql.SQL("SELECT * FROM Orders WHERE order_id={order_id}").format(order_id=sql.Literal(order_id))
        results_count, result = conn.execute(query)
    except Exception as e:
        failed = True
    finally:
        # will happen any way after code try termination or exception handling
        conn.close()
        if results_count != 1 or failed:
            return BadOrder()
        else:
            qu_res = result[0]
            return Order(qu_res['order_id'],qu_res['date'], qu_res['delivery_fee'], qu_res['delivery_address'])


def delete_order(order_id: int) -> ReturnValue:
    conn, results_count, result, final_status = None, None, None, ReturnValue.OK
    try:
        conn = Connector.DBConnector()
        query = sql.SQL("DELETE FROM Orders WHERE order_id={order_id}").format(order_id=sql.Literal(order_id))
        results_count, result = conn.execute(query)
    except Exception as e:
        final_status = ReturnValue.ERROR
    finally:
        conn.close()
        if results_count == 0:
            final_status = ReturnValue.NOT_EXISTS
        return final_status


def add_dish(dish: Dish) -> ReturnValue:
    conn, final_status = None, ReturnValue.OK
    try:
        conn = Connector.DBConnector()
        query = (sql.SQL("INSERT INTO Dishes(dish_id, name, price, is_active) "
                        "Values({dish_id}, {name}, {price}, {is_active})").format(
                            dish_id=sql.Literal(dish.get_dish_id()),
                            name=sql.Literal(dish.get_name()),
                            price=sql.Literal(dish.get_price()),
                            is_active=sql.Literal(dish.get_is_active())))

        conn.execute(query)
    except DatabaseException.ConnectionInvalid as e:
        final_status = ReturnValue.ERROR
    except DatabaseException.NOT_NULL_VIOLATION as e:
        final_status = ReturnValue.BAD_PARAMS
    except DatabaseException.CHECK_VIOLATION as e:
        final_status = ReturnValue.BAD_PARAMS
    except DatabaseException.UNIQUE_VIOLATION as e:
        final_status = ReturnValue.ALREADY_EXISTS
    except DatabaseException.FOREIGN_KEY_VIOLATION as e:
        final_status = ReturnValue.BAD_PARAMS
    except Exception as e:
        final_status = ReturnValue.ERROR
    finally:
        conn.close()
        return final_status


def get_dish(dish_id: int) -> Dish:
    conn, results_count, result, failed = None, None, None, False
    try:
        conn = Connector.DBConnector()
        query = sql.SQL("SELECT * FROM Dishes WHERE dish_id={dish_id}").format(dish_id=sql.Literal(dish_id))
        results_count, result = conn.execute(query)
    except Exception as e:
        failed = True
    finally:
        # will happen any way after code try termination or exception handling
        conn.close()
        if results_count != 1 or failed:
            return BadDish()
        else:
            return Dish(**result[0])


def update_dish_price(dish_id: int, price: float) -> ReturnValue:
    conn, results_count, result, final_status = None, None, None, ReturnValue.OK
    try:
        conn = Connector.DBConnector()
        query = sql.SQL("UPDATE Dishes SET price={price} WHERE dish_id={dish_id} AND is_active=True").format(
            price=sql.Literal(price),
            dish_id=sql.Literal(dish_id))
        results_count, result = conn.execute(query)
    except DatabaseException.ConnectionInvalid as e:
        final_status = ReturnValue.ERROR
    except DatabaseException.NOT_NULL_VIOLATION as e:
        final_status = ReturnValue.BAD_PARAMS
    except DatabaseException.CHECK_VIOLATION as e:
        final_status = ReturnValue.BAD_PARAMS
    except Exception as e:
        final_status = ReturnValue.ERROR
    finally:
        conn.close()
        if results_count == 0:
            final_status = ReturnValue.NOT_EXISTS
        return final_status


def update_dish_active_status(dish_id: int, is_active: bool) -> ReturnValue:
    conn, results_count, result, final_status = None, None, None, ReturnValue.OK
    try:
        conn = Connector.DBConnector()
        query = sql.SQL("UPDATE Dishes SET is_active={is_active} WHERE dish_id={dish_id}").format(
            is_active=sql.Literal(is_active),
            dish_id=sql.Literal(dish_id))
        results_count, result = conn.execute(query)
    except DatabaseException.ConnectionInvalid as e:
        final_status = ReturnValue.ERROR
    except DatabaseException.NOT_NULL_VIOLATION as e:
        final_status = ReturnValue.BAD_PARAMS
    except DatabaseException.CHECK_VIOLATION as e:
        final_status = ReturnValue.BAD_PARAMS
    except Exception as e:
        final_status = ReturnValue.ERROR
    finally:
        conn.close()
        if results_count == 0:
            final_status = ReturnValue.NOT_EXISTS
        return final_status


def customer_placed_order(customer_id: int, order_id: int) -> ReturnValue:
    conn, results_count, result, final_status = None, None, None, ReturnValue.OK
    try:
        conn = Connector.DBConnector()
        query = sql.SQL("INSERT INTO OrderCustomer (order_id, cust_id)"
                        " VALUES ({order_id}, {customer_id})").format(
            customer_id=sql.Literal(customer_id),
            order_id=sql.Literal(order_id),
            Null=sql.Literal(None))
        results_count, result = conn.execute(query)
    except DatabaseException.ConnectionInvalid as e:
        final_status = ReturnValue.ERROR
    except DatabaseException.NOT_NULL_VIOLATION as e:
        final_status = ReturnValue.NOT_EXISTS
    except DatabaseException.CHECK_VIOLATION as e:
        final_status = ReturnValue.NOT_EXISTS
    except DatabaseException.FOREIGN_KEY_VIOLATION as e:
        final_status = ReturnValue.NOT_EXISTS
    except DatabaseException.UNIQUE_VIOLATION as e:
        final_status = ReturnValue.ALREADY_EXISTS
    except Exception as e:
        final_status = ReturnValue.ERROR
    finally:
        conn.close()
        if results_count == 0:
            final_status = ReturnValue.NOT_EXISTS
        return final_status


def get_customer_that_placed_order(order_id: int) -> Customer:
    conn, results_count, result, failed = None, None, None, False
    try:
        conn = Connector.DBConnector()
        query = sql.SQL("SELECT C.cust_id, C.full_name, C.age, C.phone FROM Customers C INNER JOIN OrderCustomer OC ON OC.cust_id=C.cust_id WHERE OC.order_id={order_id}").format(order_id=sql.Literal(order_id))
        results_count, result = conn.execute(query)
    except Exception as e:
        failed = True
    finally:
        # will happen any way after code try termination or exception handling
        conn.close()
        if results_count != 1 or failed:
            return BadCustomer()
        else:
            return Customer(**result[0])


def order_contains_dish(order_id: int, dish_id: int, amount: int) -> ReturnValue:
    conn, final_status = None, ReturnValue.OK
    try:
        conn = Connector.DBConnector()
        query = (sql.SQL("INSERT INTO OrderDish (order_id, dish_id, current_price, amount) "
                         "( SELECT {order_id}, {dish_id}, D.price, {amount}"
                         "  FROM Dishes D"
                         "  WHERE D.dish_id={dish_id}"
                         "  AND D.is_active=TRUE)").format(
            order_id=sql.Literal(order_id),
            dish_id=sql.Literal(dish_id),
            amount=sql.Literal(amount)))

        results_count, result = conn.execute(query)
        if results_count == 0:
            final_status = ReturnValue.NOT_EXISTS
    except DatabaseException.ConnectionInvalid as e:
        final_status = ReturnValue.ERROR
    except DatabaseException.NOT_NULL_VIOLATION as e:
        final_status = ReturnValue.BAD_PARAMS
    except DatabaseException.CHECK_VIOLATION as e:
        final_status = ReturnValue.BAD_PARAMS
    except DatabaseException.UNIQUE_VIOLATION as e:
        final_status = ReturnValue.ALREADY_EXISTS
    except DatabaseException.FOREIGN_KEY_VIOLATION as e:
        final_status = ReturnValue.NOT_EXISTS
    except Exception as e:
        final_status = ReturnValue.ERROR
    finally:
        conn.close()
        return final_status


def order_does_not_contain_dish(order_id: int, dish_id: int) -> ReturnValue:
    conn, results_count, result, final_status = None, None, None, ReturnValue.OK
    try:
        conn = Connector.DBConnector()
        query = sql.SQL("DELETE FROM OrderDish"
                        " WHERE order_id={order_id}"
                        " AND dish_id={dish_id}").format(order_id=sql.Literal(order_id),dish_id=sql.Literal(dish_id))
        results_count, result = conn.execute(query)
    except Exception as e:
        final_status = ReturnValue.ERROR
    finally:
        conn.close()
        if results_count == 0:
            final_status = ReturnValue.NOT_EXISTS
        return final_status


def get_all_order_items(order_id: int) -> List[OrderDish]:
    conn, results_count, result, failed = None, None, None, False
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(
            "SELECT dish_id, amount, current_price"
            " FROM OrderDish WHERE order_id={order_id}"
            " ORDER BY dish_id ASC").format(
            order_id=sql.Literal(order_id))
        results_count, qu_result = conn.execute(query)
        result = [
            OrderDish(dish_id=row['dish_id'],amount=row['amount'],price=row['current_price']) for row in qu_result
        ]
    except Exception as e:
        failed = True
    finally:
        # will happen any way after code try termination or exception handling
        conn.close()
        return result


def customer_rated_dish(cust_id: int, dish_id: int, rating: int) -> ReturnValue:
    conn, final_status = None, ReturnValue.OK
    try:
        conn = Connector.DBConnector()
        query = (sql.SQL("INSERT INTO Ratings(cust_id, dish_id, rating) "
                         "Values({cust_id}, {dish_id}, {rating})").format(
            cust_id=sql.Literal(cust_id),
            dish_id=sql.Literal(dish_id),
            rating=sql.Literal(rating)))

        conn.execute(query)
    except DatabaseException.ConnectionInvalid as e:
        final_status = ReturnValue.ERROR
    except DatabaseException.NOT_NULL_VIOLATION as e:
        final_status = ReturnValue.BAD_PARAMS
    except DatabaseException.CHECK_VIOLATION as e:
        final_status = ReturnValue.BAD_PARAMS
    except DatabaseException.UNIQUE_VIOLATION as e:
        final_status = ReturnValue.ALREADY_EXISTS
    except DatabaseException.FOREIGN_KEY_VIOLATION as e:
        final_status = ReturnValue.NOT_EXISTS
    except Exception as e:
        final_status = ReturnValue.ERROR
    finally:
        conn.close()
        return final_status


def customer_deleted_rating_on_dish(cust_id: int, dish_id: int) -> ReturnValue:
    conn, results_count, result, final_status = None, None, None, ReturnValue.OK
    try:
        conn = Connector.DBConnector()
        query = sql.SQL("DELETE FROM Ratings"
                        " WHERE cust_id={cust_id} AND dish_id={dish_id}").format(cust_id=sql.Literal(cust_id), dish_id=sql.Literal(dish_id))
        results_count, result = conn.execute(query)
    except DatabaseException.FOREIGN_KEY_VIOLATION as e:
        final_status = ReturnValue.NOT_EXISTS
    except Exception as e:
        final_status = ReturnValue.ERROR
    finally:
        conn.close()
        if results_count == 0:
            final_status = ReturnValue.NOT_EXISTS
        return final_status

def get_all_customer_ratings(cust_id: int) -> List[Tuple[int, int]]:
    conn, results_count, result, failed = None, None, None, False
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(
            "SELECT dish_id, rating"
            " FROM Ratings WHERE cust_id={cust_id}"
            " ORDER BY dish_id ASC").format(
            cust_id=sql.Literal(cust_id))
        results_count, qu_result = conn.execute(query)
        result = [
            (row['dish_id'], row['rating']) for row in qu_result
        ]
    except Exception as e:
        failed = True
    finally:
        # will happen any way after code try termination or exception handling
        conn.close()
        return result
# ---------------------------------- BASIC API: ----------------------------------

# Basic API


def get_order_total_price(order_id: int) -> float:
    conn, results_count, result, failed = None, None, [], False
    try:
        conn = Connector.DBConnector()
        query = sql.SQL("SELECT subtotal FROM OrdersPrices WHERE order_id={order_id}").format(order_id=sql.Literal(order_id))
        results_count, result = conn.execute(query)
    except Exception as e:
        failed = True
    finally:
        # will happen any way after code try termination or exception handling
        conn.close()
        if results_count != 1 or failed:
            return 0
        else:
            qu_res = result[0]
            return float(qu_res['subtotal'])

def get_customers_spent_max_avg_amount_money() -> List[int]:
    conn, results_count, result, failed = None, None, [], False
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(
            """
            SELECT cust_id FROM
                (SELECT OC.cust_id AS cust_id, AVG(COALESCE(OP.subtotal, 0)) AS avg_spent
                 FROM OrderCustomer OC JOIN OrdersPrices OP on OC.order_id = OP.order_id
                 GROUP BY OC.cust_id ) AS CustomerAvg
                WHERE avg_spent = (SELECT MAX(avg_spent2) FROM (SELECT AVG(COALESCE(OP.subtotal, 0)) as avg_spent2 FROM OrderCustomer OC JOIN OrdersPrices OP on OC.order_id = OP.order_id
                 GROUP BY OC.cust_id))
                ORDER BY cust_id ASC
            """)
        results_count, qu_result = conn.execute(query)
        result = [
            row['cust_id'] for row in qu_result
        ]
    except Exception as e:
        failed = True
    finally:
        # will happen any way after code try termination or exception handling
        conn.close()
        return result


def get_most_ordered_dish_in_period(start: datetime, end: datetime) -> Dish:
    conn, results_count, result, failed = None, None, None, False
    try:
        conn = Connector.DBConnector()

        query = sql.SQL("SELECT D.dish_id, D.name, D.price, D.is_active, SUM(OD.amount) as tot_amount"
                        " FROM (SELECT * FROM Orders WHERE date >= {start} AND date <= {end}) as O"
                        " JOIN OrderDish as OD ON O.order_id = OD.order_id"
                        " JOIN Dishes as D ON OD.dish_id=D.dish_id"
                        " GROUP BY D.dish_id"
                        " ORDER BY tot_amount DESC, D.dish_id ASC LIMIT 1").format(
            start=sql.Literal(start),
            end=sql.Literal(end))
        results_count, result = conn.execute(query)
    except Exception as e:
        failed = True
    finally:
        # will happen any way after code try termination or exception handling
        conn.close()
        if results_count != 1 or failed:
            return BadDish()
        else:
            qu_res = result[0]
            return Dish(dish_id=qu_res['dish_id'], name=qu_res['name'], price=qu_res['price'], is_active=qu_res['is_active'])

def did_customer_order_top_rated_dishes(cust_id: int) -> bool:
    conn, results_count, result, failed = None, None, None, False
    try:
        conn = Connector.DBConnector()
        query = sql.SQL("""SELECT EXISTS (
                         SELECT 1 FROM OrderDish OD JOIN OrderCustomer OC ON OD.order_id=OC.order_id 
                         WHERE OC.cust_id = {cust_id} AND
                         OD.dish_id IN (
                          SELECT NewRates.dish_id FROM
                          (SELECT D.dish_id as dish_id, COALESCE(R.rating, 3.0) as new_rating FROM Dishes D LEFT JOIN Ratings R ON D.dish_id = R.dish_id) as NewRates
                          GROUP BY NewRates.dish_id
                          ORDER BY AVG(new_rating) DESC, NewRates.dish_id ASC
                          LIMIT 5
                         )
                        ) AS did_order""").format(
            cust_id=sql.Literal(cust_id))
        results_count, result = conn.execute(query)
    except Exception as e:
        failed = True
    finally:
        # will happen any way after code try termination or exception handling
        conn.close()
        if results_count != 1 or failed:
            return False
        else:
            qu_res = result[0]
            return qu_res['did_order']


# ---------------------------------- ADVANCED API: ----------------------------------

# Advanced API


def get_customers_rated_but_not_ordered() -> List[int]:
    conn, results_count, result, failed = None, None, None, False
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(
            """
            SELECT DISTINCT R.cust_id
            FROM ratings R
            WHERE R.rating < 3
              AND R.dish_id IN (
                SELECT dish_id
                FROM (
                    SELECT D.dish_id, COALESCE(AVG(R2.rating), 3) AS avg_rating
                    FROM dishes D
                    LEFT JOIN ratings R2 ON D.dish_id = R2.dish_id
                    GROUP BY D.dish_id
                    ORDER BY avg_rating ASC, D.dish_id ASC
                    LIMIT 5
                )
              )
              AND NOT EXISTS (
                SELECT 1
                FROM OrderCustomer OC
                JOIN orderdish OD ON OC.order_id = OD.order_id
                WHERE OC.cust_id = R.cust_id
                  AND OD.dish_id = R.dish_id
              )
            ORDER BY R.cust_id ASC
            """)
        results_count, qu_result = conn.execute(query)
        result = [
            row['cust_id'] for row in qu_result
        ]
    except Exception as e:
        failed = True
    finally:
        # will happen any way after code try termination or exception handling
        conn.close()
        return result


def get_non_worth_price_increase() -> List[int]:
    conn, results_count, result, failed = None, None, None, False
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(
            """
            SELECT CurrentPriceData.dish_id
            FROM (
            SELECT D.dish_id, D.price AS current_price, AVG(OD.amount) * D.price AS current_avg_profit
            FROM Dishes D
            JOIN orderdish OD ON D.dish_id = OD.dish_id AND D.price = OD.current_price
            WHERE D.is_active = TRUE
            GROUP BY D.dish_id, D.price
            ) AS CurrentPriceData
            JOIN (
                SELECT
                    OD.dish_id,
                    OD.current_price AS old_price,
                    AVG(OD.amount) * OD.current_price AS old_avg_profit
                FROM orderdish OD
                JOIN dishes D ON OD.dish_id = D.dish_id
                WHERE OD.current_price < D.price  -- Ensures the price in the order is lower than current price
                GROUP BY OD.dish_id, OD.current_price, OD.dish_id
                ORDER BY OD.dish_id ASC
            ) AS PastPriceData
            ON CurrentPriceData.dish_id = PastPriceData.dish_id
            WHERE PastPriceData.old_price < CurrentPriceData.current_price
            GROUP BY CurrentPriceData.dish_id, CurrentPriceData.current_avg_profit
            HAVING CurrentPriceData.current_avg_profit < MAX(PastPriceData.old_avg_profit)
            ORDER BY CurrentPriceData.dish_id ASC
            """)
        results_count, qu_result = conn.execute(query)
        result = [
            row['dish_id'] for row in qu_result
        ]
    except Exception as e:
        failed = True
    finally:
        # will happen any way after code try termination or exception handling
        conn.close()
        return result


def get_cumulative_profit_per_month(year: int) -> List[Tuple[int, float]]:
    conn, results_count, result, failed = None, None, None, False
    try:
        conn = Connector.DBConnector()
        query = sql.SQL("""
        WITH RECURSIVE all_months AS (
            SELECT 1 as i
            UNION
            SELECT i+1
            FROM all_months
            WHERE i < 12
        ) SELECT i as month, COALESCE((SELECT SUM(OP.subtotal) FROM Orders as O JOIN OrdersPrices as OP ON O.order_id = OP.order_id WHERE EXTRACT(YEAR FROM O.date) = {year} AND EXTRACT(MONTH FROM O.date) <= am.i ), 0.0) as total FROM all_months as am
        ORDER BY month DESC
        """).format(year=sql.Literal(year))
        results_count, qu_result = conn.execute(query)
        result = [
            (row['month'], float(row['total'])) for row in qu_result
        ]
    except Exception as e:
        failed = True
    finally:
        # will happen any way after code try termination or exception handling
        conn.close()
        return result

def get_potential_dish_recommendations(cust_id: int) -> List[int]:
    conn, results_count, result, failed = None, None, None, False
    try:
        conn = Connector.DBConnector()
        query = sql.SQL("""
        WITH RECURSIVE similar_customers AS (
            SELECT R2.cust_id as cust_id
            FROM Ratings as R1 JOIN Ratings as R2 ON R1.dish_id = R2.dish_id
            WHERE R1.cust_id={cust_id}
                AND R1.rating >= 4 AND R2.rating >= 4
            UNION
            SELECT R4.cust_id as cust_id
            FROM Ratings as R3 INNER JOIN similar_customers as S ON R3.cust_id = S.cust_id
                JOIN Ratings as R4 ON R3.dish_id = R4.dish_id
            WHERE R3.rating >= 4 AND R4.rating >= 4
        ) SELECT DISTINCT R5.dish_id as dish_id FROM similar_customers as S2
        INNER JOIN Ratings as R5 ON S2.cust_id = R5.cust_id
        WHERE S2.cust_id <> {cust_id} AND R5.dish_id NOT IN (
            SELECT dish_id FROM OrderDish as OD LEFT JOIN OrderCustomer as OC ON OD.order_id = OC.order_id
                           WHERE OC.cust_id = {cust_id}
            )
            AND R5.rating >= 4
            ORDER BY dish_id ASC
                        """).format(cust_id=sql.Literal(cust_id))
        results_count, qu_result = conn.execute(query)
        result = [
            row['dish_id'] for row in qu_result
        ]
    except Exception as e:
        failed = True
    finally:
        # will happen any way after code try termination or exception handling
        conn.close()
        return result


# ---------------------------------- Utility: ----------------------------------

# Timestamps for SQL

def format_timestamp_for_sql(dt: datetime) -> str:
    if dt is None:
        return None
    return dt.strftime('%Y-%m-%d %H:%M:%S')

# ---------------------------------- Main: ----------------------------------

if __name__ == '__main__':
    drop_tables()
    create_tables()
    clear_tables()
    add_customer(Customer(1, 'bob', 21, "0123456789"))
    add_customer(Customer(2, 'alice', 19, "1122334455"))
    add_customer(Customer(3, 'george', 50, "0533333333"))
    add_order(Order(1, datetime.now(), 15, "Haifa"))
    add_order(Order(2, datetime.now(), 20, "Tel Aviv"))
    add_dish(Dish(1, "pizza", 50, True))
    add_dish(Dish(2, "burger", 30, True))
    add_dish(Dish(3, "salad", 20, False))
    add_dish(Dish(4, "banana", 30, True))
    order_contains_dish(1,1,2)
    order_contains_dish(1,2,3)
    order_contains_dish(2,3,4)

    customer_placed_order(1,1)

    res1 = get_customer_that_placed_order(1)
    print(f" Customer that ordered order 1 is {res1}")

    res2 = get_customer_that_placed_order(2)
    print(f" Customer that ordered order 2 is  {res2}")

    res3 = get_all_order_items(1)
    print(f" All order items are {res3}")

    res4 = get_order_total_price(1)
    print(f" Total price is {res4}")

    res5 = get_order_total_price(2)
    print(f" Total price is {res5}")

    customer_rated_dish(1,1,1)
    customer_rated_dish(1,2,4)
    customer_rated_dish(2,3,4)
    customer_rated_dish(2,2,5)
    customer_rated_dish(3,3,3)

    customer_deleted_rating_on_dish(1,2)

    res6 = get_all_customer_ratings(1)
    print(f" All customer ratings are {res6}")

    res7 = get_customers_spent_max_avg_amount_money()
    print(f" Customer spent max amount is {res7}")

    res8 = get_customers_rated_but_not_ordered()
    print(f" Customer rated but not ordered is {res8}")

    add_order(Order(5, datetime.now(), 15, "Haifa"))
    add_order(Order(6, datetime.now(), 20, "Tel Aviv"))
    add_order(Order(7, datetime.now(), 30, "Haifa"))
    add_order(Order(8, datetime.now(), 40, "Tel Aviv"))

    update_dish_price(4,50)
    order_contains_dish(5,4,1)
    order_contains_dish(6,4,2)

    update_dish_price(4,40)
    order_contains_dish(7,4,2)
    order_contains_dish(8,4,2)

    update_dish_price(4,50)

    res9 = get_non_worth_price_increase()
    print(f" Non-worth price is {res9}")

    conn = Connector.DBConnector()
    print(get_customer(1))
    print(get_order(1))

    delete_customer(1)

    res10 = get_customer(1)
    print(f" Customer 1 is {res10}")

    res11 = order_contains_dish(1,1,5)
    print(f" Order 1 adding dish 1 results in is {res11}")
    res12 = order_contains_dish(1,2,3)
    print(f" Order 1 adding dish 2 results in is {res12}")
    res13 = order_contains_dish(6,3,4)
    print(f" Order 6 adding dish 3 results in is {res13}")
    res14 = order_contains_dish(10,2,4)
    print(f" Order 10 adding dish 3 results in is {res14}")

    res15 = add_customer(Customer(2, 'charlie', 34, "0123456789"))
    print(f" Customer 2 is {res15}")

    res16 = customer_deleted_rating_on_dish(2,3)
    print(f" Customer 2 deleted rating of dish 3 {res16}")
    res17 = customer_deleted_rating_on_dish(2,4)
    print(f" Customer 2 deleted rating of dish 4 {res17}")
    res18 = customer_deleted_rating_on_dish(3,4)
    print(f" Customer 3 deleted rating of dish 4 {res18}")


    # 2. Define our period
    start_date = datetime(2023, 1, 1, 10, 0,0)
    end_date = datetime(2023, 1, 1, 20, 0,0)

    # 3. Add Orders
    # Dish 1: 2 orders inside the period
    order1 = Order(101, datetime(2023, 1, 1, 12, 1,0), 10,"Abbbb")
    res19 = add_order(order1)
    order_contains_dish(101,1,3)

    order2 = Order(102, datetime(2023, 1, 1, 15, 0,0), 10,"Accccc")
    add_order(order2)
    order_contains_dish(102,1,1)

    # Dish 2: 1 order inside, 2 orders outside the period
    order3 = Order(103, datetime(2023, 1, 1, 16, 0,0), 10,"Adddddd")  # INSIDE
    add_order(order3)
    order_contains_dish(103,2,1)

    order4 = Order(104, datetime(2023, 1, 1, 22, 0,0), 10,"Aeeeeee")  # OUTSIDE
    add_order(order4)
    order_contains_dish(104,1,1)

    # 4. Execution
    result = get_most_ordered_dish_in_period(start_date, end_date)

    # 5. Assertion
    print(f" Most ordered dishes are {result}")

    pass