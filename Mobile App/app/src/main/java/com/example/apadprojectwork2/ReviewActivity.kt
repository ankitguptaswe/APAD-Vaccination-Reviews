package com.example.apadprojectwork2

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import androidx.appcompat.app.ActionBar
import androidx.recyclerview.widget.LinearLayoutManager
import com.android.volley.Response
import com.android.volley.toolbox.StringRequest
import com.android.volley.toolbox.Volley
import com.google.gson.Gson
import kotlinx.android.synthetic.main.activity_review.*
import kotlinx.android.synthetic.main.activity_review.recyclerView_main
import kotlinx.android.synthetic.main.review_row.*

class ReviewActivity : AppCompatActivity() {
    private  lateinit var actionBar: ActionBar

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_review)
        recyclerView_main.layoutManager = LinearLayoutManager(this)
        actionBar = supportActionBar!!
        actionBar.title = "Reviews"
        fetchReviews()
    }

    override fun onResume() {
        super.onResume()
        setContentView(R.layout.activity_review)
        recyclerView_main.layoutManager = LinearLayoutManager(this)
        fetchReviews()
    }

    fun fetchReviews() {
        val intent = getIntent()
        theme_Name.text = intent.getStringExtra("Theme")
        val queue = Volley.newRequestQueue(this)
        val url = "https://apad-vaccine-reviews.uc.r.appspot.com/themes/".plus(theme_Name.text)
        val stringRequest = object: StringRequest(
            Method.GET, url,
            Response.Listener { response ->
                val strResp = response.toString()
                var list: List<String> = strResp.drop(1).dropLast(1).dropLast(1).split("},").map { it.trim() }
                val gson = Gson()
                val reviews : MutableList<Reviews> = arrayListOf()
                for (item in list) {
                    reviews.add(gson.fromJson(item.plus("}"), Reviews::class.java))
                }
                runOnUiThread {
                    recyclerView_main.adapter = ReviewAdapter(reviews)
                }
            },
            Response.ErrorListener {  })
        {
            override fun getHeaders(): MutableMap<String, String> {
                val headers = HashMap<String, String>()
                headers["source"] = "android"
                return headers
            }
        }
        queue.add(stringRequest)
    }
}