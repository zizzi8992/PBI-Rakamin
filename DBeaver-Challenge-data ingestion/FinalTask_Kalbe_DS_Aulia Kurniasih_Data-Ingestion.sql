-- FinalTask_Kalbe_DS_Aulia Kurniasih
-- query 1 : Berapa rata-rata umur customer jika dilihat dari marital statusnya ?

SELECT 
    CASE 
        WHEN marital_status ISNULL THEN 'Unknown'
        ELSE marital_status 
    END AS marital_status,
    AVG(age) AS average_age
FROM customer
GROUP BY marital_status;


-- query 2: Berapa rata-rata umur customer jika dilihat dari gender nya ?

SELECT
    CASE
        WHEN gender = '0' THEN 'female'
        WHEN gender = '1' THEN 'male'
    END AS gender_label,
    AVG(age) AS average_age
FROM customer
GROUP BY gender;


-- query 3: Tentukan nama store dengan total quantity terbanyak!


SELECT store.storename, sum(transaction.qty) AS total_qty
FROM store
JOIN TRANSACTION ON transaction.storeid  = store.storeid
GROUP BY store.storename 
ORDER BY total_qty DESC
LIMIT 1;



-- query 4: : Tentukan nama produk terlaris dengan total amount terbanyak!


SELECT products.product_name , sum(transaction.totalamount) AS total_amount
from products
JOIN TRANSACTION ON transaction.productid = products.productid 
GROUP BY products.product_name
ORDER BY total_amount DESC
LIMIT 1;


