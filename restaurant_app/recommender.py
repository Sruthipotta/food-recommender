import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.db.models import Count, Sum


class RestaurantRecommender:
    def __init__(self, user, Order, OrderItem, FoodItem):
        self.user = user
        self.Order = Order
        self.OrderItem = OrderItem
        self.FoodItem = FoodItem

    def _prepare_order_data(self):
        
        order_items = self.OrderItem.objects.select_related('order', 'food_item').all()

        df = pd.DataFrame(list(order_items.values(
            'order__customer_id',
            'food_item_id',
            'food_item__name',
            'food_item__category',
            'quantity'
        )))

        df.columns = [
            'user_id',
            'food_item_id',
            'food_name',
            'category',
            'quantity'
        ]

        return df

    def collaborative_filtering(self):
        df = self._prepare_order_data()

        user_item_matrix = df.pivot_table(
            index='user_id',
            columns='food_item_id',
            values='quantity',
            fill_value=0
        )

        user_similarity = cosine_similarity(user_item_matrix)
        user_similarity_df = pd.DataFrame(
            user_similarity,
            index=user_item_matrix.index,
            columns=user_item_matrix.index
        )

        if self.user.id not in user_similarity_df.index:
            return []

        similar_users = user_similarity_df.loc[self.user.id].sort_values(ascending=False)[1:6]

        # Get items liked by similar users
        recommended_items = df[
            df['user_id'].isin(similar_users.index) &
            ~df['food_item_id'].isin(
                self.OrderItem.objects.filter(order__customer=self.user)
                .values_list('food_item_id', flat=True)
            )
        ]

        return recommended_items['food_item_id'].unique().tolist()

    def content_based_filtering(self):

        food_items = self.FoodItem.objects.all()

        user_categories = (
            self.OrderItem.objects
            .filter(order__customer=self.user)
            .values('food_item__category')
            .annotate(count=Count('food_item__category'))
            .order_by('-count')
        )

        if not user_categories:
            return list(self.FoodItem.objects.order_by('?')[:10].values_list('id', flat=True))

        food_data = pd.DataFrame(list(food_items.values('id', 'name', 'description', 'category')))
        food_data['content'] = food_data['name'] + ' ' + food_data['description'] + ' ' + food_data['category']

        vectorizer = TfidfVectorizer(stop_words='english')
        content_matrix = vectorizer.fit_transform(food_data['content'])

        # Find similar items based on content
        preferred_categories = [cat['food_item__category'] for cat in user_categories[:2]]

        similar_items = food_data[food_data['category'].isin(preferred_categories)]
        similar_matrix = vectorizer.transform(similar_items['content'])

        content_similarities = cosine_similarity(content_matrix, similar_matrix)

        top_indices = content_similarities.mean(axis=1).argsort()[::-1][:10]

        return food_data.iloc[top_indices]['id'].tolist()

    def popularity_based(self):
        popular_items = (
            self.OrderItem.objects
            .values('food_item')
            .annotate(total_quantity=Sum('quantity'))
            .order_by('-total_quantity')[:10]
        )

        return [item['food_item'] for item in popular_items]

    def get_recommendations(self, n_recommendations=10):
        collaborative_recs = self.collaborative_filtering()
        content_recs = self.content_based_filtering()
        popular_recs = self.popularity_based()

        all_recommendations = list(set(
            collaborative_recs +
            content_recs +
            popular_recs
        ))

        existing_orders = set(
            self.OrderItem.objects
            .filter(order__customer=self.user)
            .values_list('food_item_id', flat=True)
        )

        recommendations = [
            rec for rec in all_recommendations
            if rec not in existing_orders
        ]

        return recommendations[:n_recommendations]
