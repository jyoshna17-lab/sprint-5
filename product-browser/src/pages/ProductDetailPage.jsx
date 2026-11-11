import {Link, useParams} from 'react-router' //used to take the value from the path
import { useEffect, useState } from "react";

function ProductDetailPage(){
        const {id} = useParams() ; 
    const [product , setProducts] = useState(null)

    
    useEffect(()=> {
        async function loadProducts(){
            const res = await fetch(`https://dummyjson.com/products/${id}`);
            const data = await res.json();
            setProducts(data); // we are storing the data in a state. setProducts is a functions
        }
        loadProducts();
    }, [id]);

    

    if (!product) return<p>Loading........</p>


    return (
    <div>
        <Link to="/">Back to products</Link>
       <ul>
            <li key = {product.id} >
                <img src = {product.thumbnail}></img>
                <h3>{product.title} </h3>
                <p>Price: ${product.price}</p>
                <p>Rating: {product.rating}</p>
                <p>Category: {product.category}</p>
                <p>Stock: {product.stock}</p>
                <h3>Reviews</h3>
                <ul>
                    {product.reviews.map((review) => (
                        <li
                            key = {review.reviewerEmail}>
                                {review.reviewerName} : {review.comment}
                        </li>
                    ))}
                </ul>
                </li>
        </ul>
    </div>
    );
}

    export default ProductDetailPage;