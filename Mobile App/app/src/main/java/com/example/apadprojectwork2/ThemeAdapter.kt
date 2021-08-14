package com.example.apadprojectwork2

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.squareup.picasso.Picasso
import kotlinx.android.synthetic.main.theme_row.*
import kotlinx.android.synthetic.main.theme_row.view.*

class ThemeAdapter(val themes: Themes): RecyclerView.Adapter<ThemeViewHolder>() {
    override fun getItemCount(): Int {
        return themes.themes.count()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ThemeViewHolder {
        val layoutInflater = LayoutInflater.from(parent.context)
        val cellForRow = layoutInflater.inflate(R.layout.theme_row, parent, false)
        return ThemeViewHolder(cellForRow)
    }

    override fun onBindViewHolder(holder: ThemeViewHolder, position: Int) {
        holder?.view?.textView_review_title?.text = themes.themes.get(position)
        holder?.view?.textView_review_description?.text = themes.descriptions.get(position)
        val thumbnailImageView = holder?.view?.imageView_review_thumbnail
        val Url = "https://storage.googleapis.com/apad-group8-bucket/img/themes"
        val imageUrl = Url.plus("/").plus(themes.pictures.get(position))
        Picasso.with(holder?.view?.context).load(imageUrl).into(thumbnailImageView)
    }
}

class ThemeViewHolder(val view: View): RecyclerView.ViewHolder(view) {
}