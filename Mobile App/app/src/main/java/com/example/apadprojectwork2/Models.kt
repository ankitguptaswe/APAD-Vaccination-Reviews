package com.example.apadprojectwork2

class Themes(val themes: List<String>, val descriptions: List<String>, val pictures: List<String>)

class Reviews(
    val _id: String,
    val user_token: String,
    val title: String,
    val theme: String,
    val rating: Int,
    val picture: String,
    val description: String,
    val tags: String,
    val geo_location: List<Double>
) {
    override fun toString(): String {
        return "_id: ${this._id}, user_token: ${this.user_token}, title: ${this.title}" +
                ", theme: ${this.theme}, rating: ${this.rating}, picture: ${this.picture}" +
                ", description: ${this.description}, tags: ${this.tags}" +
                ", geo_location: ${this.geo_location}"
    }
}
