package com.example.apadprojectwork2

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.squareup.picasso.Picasso
import kotlinx.android.synthetic.main.activity_review.view.*
import kotlinx.android.synthetic.main.review_row.view.*

class ReviewAdapter(val reviews: List<Reviews>): RecyclerView.Adapter<ReviewViewHolder>() {
    override fun getItemCount(): Int {
        return reviews.count()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ReviewViewHolder {
        val layoutInflater = LayoutInflater.from(parent.context)
        val cellForRow = layoutInflater.inflate(R.layout.review_row, parent, false)
        return ReviewViewHolder(cellForRow)
    }

    override fun onBindViewHolder(holder: ReviewViewHolder, position: Int) {
        holder?.view?.tv_title?.text = reviews[position].title
        holder?.view?.tv_description?.text = reviews[position].description
        holder?.view?.tv_geo_location?.text = reviews[position].geo_location.toString()
        holder?.view?.tv_rating?.text = reviews[position].rating.toString()
        holder?.view?.tv_tags?.text = reviews[position].tags
        val thumbnailImageView = holder?.view?.tv_picture
        val Url = "https://storage.googleapis.com/apad-group8-bucket/img/reviews"
        val imageUrl = Url.plus("/").plus(reviews[position].picture)
        Picasso.with(holder?.view?.context).load(imageUrl).into(thumbnailImageView)
    }
}

class ReviewViewHolder(val view: View): RecyclerView.ViewHolder(view) {
}